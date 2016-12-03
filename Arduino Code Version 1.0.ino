/*
    Author: Deepak Kumar
    Email: kumardeepakr3@gmail.com
    Project Report: http://home.iitk.ac.in/~deepakr/reports/BiometricFingerprint.pdf
    I took some portion of the code from somewhere on internet, which I forgot.
    So if anyone finds the place from where, let me know to add to the contributors
*/


//Board USED = Arduino Mega 2560
//Using required Macros for Command codes
#define Openfps 0x01
#define Closefps 0x02
#define UsbInternalCheck 0x03
#define ChangeBaudrate 0x04
#define CmosLED 0x12
#define GetEnrollCountfps 0x20
#define CheckEnrolledfps 0x21
#define EnrollStartfps 0x22
#define Enroll1fps 0x23
#define Enroll2fps 0x24
#define Enroll3fps 0x25
#define IsPressFingerfps 0x26
#define DeleteId 0x40
#define DeleteALL 0x41
#define Verify 0x50
#define Identify 0x51
#define VerifyTemplate 0x52
#define IdentifyTemplate 0x53
#define CaptureFingerfps 0x60
#define MakeTemplate 0x61
#define GetImage 0x62
#define GetRawImage 0x63
#define GetTemplate 0x70
#define SetTemplate 0x71
#define GetDatabaseStart 0x72
#define GetDatabaseEnd 0x73


//Defining requied global variables
int led = 13;
int rec_ID = 200;
int enrollid = 0;
byte highbyte = 0;
byte lowbyte = 0; 

byte highcheck = 0;
byte lowcheck = 0;

byte response = 0;

word checksum = 0;
word checksumReply = 0;
word parameterin = 0;

boolean communicationError = false;
boolean checksumCorrect = true; 
boolean ack = false;

byte lbyte = 0;
byte hbyte = 0;
byte checklbyte = 0;
byte checkhbyte = 0;

int commandval = 0;
int unique_id;
String sendstring;

const int transmitDelay = 500;




//The setup function runs only once when the Arduino is powered on
void setup()
{
    pinMode(led, OUTPUT);         //Define the PIN 13 i.e. led as output pin, arduino on-board LED
    digitalWrite(led, LOW);       // Turn off the LED at pin 13
  
    Serial.begin(9600);           // Begin serial communication for hard wired serial port at 9600 bps(bits per second)
    Serial2.begin(9600);          // Begin serial communication with fps(finger print sensor) at 9600 bps
    Serial3.begin(9600);          // Begin serial communication with bluetooth module at 9600 bps
    scannerCommand(Openfps, 0);   // Switch on the fingerprint scanner.
    scannerCommand(CmosLED, 1);   // Switch on the LED on the fps
 
}


//This part of the code iterates over again and again
void loop()
{


   if(Serial3.available() > 0)               // If there is any serial data command packet available on the bluetooth
   {
     
         commandval = Serial3.parseInt();       // Get the integer form of the command packet string
         rec_ID = commandval-((commandval/1000)*1000);  // Get the received value's ID portion
         
         if((commandval/1000) == 1)             // If the thousands digit is 1 -> marking attendence condition
         {
             blink_LED();
             unique_id = IDVerify();              // Get the unique ID of the finger pressed.
             blink_LED();                         
             get_str();                           // Sends the string having the unique_ID via bluetooth to the PC
         }
      
         if((commandval/1000) == 2)               // Enroll Command
         {
             blink_LED();
             enroll();
             unique_id = enrollid;
             get_str();
             blink_LED();
         }
      
         if((commandval/1000) == 3)             // Delete Command for rec_ID
         {
             blink_LED();
             deleteID();
             unique_id = rec_ID;
             get_str();
             blink_LED();
         }
      
         if((commandval/1000) == 4)              // Delete all IDs in fps
         {
             blink_LED();
             deleteall();
             unique_id = rec_ID;
             get_str();
             blink_LED();
         }
      
         while(Serial3.available() > 0)
         {Serial3.read();}  //Flush out if there is anything else in the Serial port of bluetooth module
     
   }

}






//OK, now here are the functions I used.


//This function blinks the LED on the Arduino Board
void blink_LED()
{
      digitalWrite(led, HIGH);
      delay(500);
      digitalWrite(led, LOW);
      delay(500); 
}


//This is the function that sends command data to the device
void scannerCommand(byte com, int param)
{ 
     valueToWORD(param); //converts the parameter into lowbyte and highbyte
     calcChecksum(com, highbyte, lowbyte); //calculates checksum and puts it into lowcheck and highcheck
 
     Serial2.write(0x55);        // REQ: Command start code1       BYTE
     Serial2.write(0xaa);        // REQ: Command start code2       BYTE
     Serial2.write(0x01);        // REQ: Device ID lowerbyte       WORD
     Serial2.write(0x00);        // REQ: Device ID higherbyte
     Serial2.write(lowbyte);     // Parameter lowerbyte            DWORD 
     Serial2.write(highbyte);    // Parameter higherbyte
     Serial2.write(0x00);        // Parameter next higherbyte
     Serial2.write(0x00);        // Parameter next higherbyte
     Serial2.write(com);         // Command lowerbyte               WORD
     Serial2.write(0x00);        // Command higherbyte
     Serial2.write(lowcheck);    // Checksum                        WORD
     Serial2.write(highcheck);   // Checksum
     GetAcknowledge();           // Get response from the fingerprint scanner
}



void GetAcknowledge()
{ //This is the function that receives data (Response Packet) from the device.
     communicationError = false;
  
     while(Serial2.available() == 0){} //Check if serial communication is available
     delay(transmitDelay); //wait for a minor time
  
     if(Serial2.read() == 0x55){} // REQ: Response start code1 BYTE
     else {communicationError = true;}

     if(Serial2.read() == 0xAA){} //REQ: Response start code2 BYTE
     else {communicationError = true;}

     if(Serial2.read() == 0x01){} // REQ: Device ID lowerbyte WORD
     else {communicationError = true;}

     if(Serial2.read() == 0x00){} // REQ: Device ID higherbyte
     else {communicationError = true;}

     lbyte = Serial2.read();             // Parameter lowerbyte DWORD
     hbyte = Serial2.read();             // Parameter higherbyte
     Serial2.read();                     // Parameter's 3rd highest byte
     Serial2.read();                     // Parameter's 4th highest byte
     parameterin = word(hbyte, lbyte);   // Parameter converted to word

     response = Serial2.read();          // Read response lowerbyte WORD
     Serial2.read();                     // Read response higherbyte
  
     if(response == 0x30){ack = true;}   // Check the FPS acknowledgement
     else {ack = false;}

     checklbyte = Serial2.read();        // REQ: Checksum lowerbyte
     checkhbyte = Serial2.read();        // REQ: Checksum higherbyte

     checksumReply = word(checkhbyte, checklbyte);

     if(checksumReply == 256 + lbyte + hbyte + response) // Verify if checksum is correct
     {checksumCorrect = true;} 
     else
     {checksumCorrect = false;} 

}

void calcChecksum(byte c, byte h, byte l)
{ //Also uses this function I have shown above
     checksum = 256 + c + h + l; //adds up all the bytes sent
     highcheck = highByte(checksum); //then turns this checksum which is a word into 2 bytes
     lowcheck = lowByte(checksum);
}

void valueToWORD(int v)
{ //turns the word you put into it (the paramter in the code above) to two bytes
     highbyte = highByte(v); //the high byte is the first byte in the word
     lowbyte = lowByte(v); //the low byte is the last byte in the word (there are only 2 in a word)
}




void deleteID()
{
     scannerCommand(DeleteId, rec_ID);
}

void deleteall()
{
     scannerCommand(DeleteALL, 0);
}


//This funciton sends a string of the unique ID back to the calling device.
void get_str() 
{
     if (unique_id < 10)
      {
            sendstring = String("00"+String(unique_id)); //The unique_id must be a string of three digits. It ranges from 0-199
      }
      else
      {
            if (unique_id < 100)
            {
                 sendstring = String("0"+String(unique_id));
            }
            else
            {
                 sendstring = String(unique_id);
            }
      }
   
      Serial3.print(sendstring);    // Send the string to the calling device. This string is of the unique ID to be sent. The string is composed of 3 bytes
      Serial.println(sendstring);   // Check on the hard wired serial port for the string that is sent
      delay(500);
}



//This function verifies if the finger pressed on the Fingerprint module is correct
int IDVerify()       
{
  
     while(1)
     {
          scannerCommand(IsPressFingerfps, 0);        //Is finger is pressed on the fps
          if(parameterin == 0)                        // ^If yes
          {
                 scannerCommand(CaptureFingerfps, 0);      // Capture the image of the finger
                 scannerCommand(Identify, 0);              // Identify the finger that is pressed. If it is present in the database, then parameterin returns the unique_ID in [0,199]
                 if(parameterin < 200)                     // If verified ID
                 {
                       Serial.print("Verified ID");
                       Serial.println(parameterin);
                       return parameterin;
                 }
                 else
                 {
                       Serial.println("Finger not found");
                       return 250;                              // Return a value Greater than 200
                 } 
      
          }
     } 
    
}  
  


void enroll()
{
    enrollid = 0;
    bool usedid = true;
    while (usedid == true)  // While there is already a template stored at usedid continue looping to find a empty ID
    {
         scannerCommand(CheckEnrolledfps, enrollid); // Check if enrollid is already present in the Template database
         usedid = ack;                               // ack is true if enrollid is present in the Template database
         if(usedid == true) enrollid++;              // Check for the next enrollid
    }
    scannerCommand(EnrollStartfps, enrollid);     // Start enrolling at the given enrollid
    
    Serial.print("Press Finger to Enroll #");
    Serial.println(enrollid);
    
    scannerCommand(IsPressFingerfps, 0);  // Checks if finger is pressed
    while(!(parameterin == 0))            // parameterin is 0 -> Finger is pressed. parameterin is non-zero -> Finger not pressed. Continue this loop till finger is pressed
    {
         delay(100);
         scannerCommand(IsPressFingerfps, 0);
    }
    
    scannerCommand(CaptureFingerfps, 1);  // Take a fingerprint pic of high quality
    bool bret = ack;                      // ack is true if fingerprint was captured, else ack is false
    int iret = 0;
    
    if (bret != false)
    {
              Serial.println("Remove Finger");
              scannerCommand(Enroll1fps, 0);    // Create Template 1 of the finger just captured
       
              scannerCommand(IsPressFingerfps, 0);  // Checks if finger is pressed
              while(parameterin == 0)               // Loop till the finger is not removed
              {
                delay(100);
                scannerCommand(IsPressFingerfps, 0);
              }    
       
              Serial.println("Press the same finger again");
       
              scannerCommand(IsPressFingerfps, 0);  // Checks if finger is pressed
              while(!(parameterin == 0))            // Loop till the finger is pressed again
              {
                delay(100);
                scannerCommand(IsPressFingerfps, 0);
              }
    
              scannerCommand(CaptureFingerfps, 1);  // Capture finger for template 2
              bret = ack;
       
              if(bret != false)
              {
                          Serial.println("Remove Finger");
                          scannerCommand(Enroll2fps, 0); // Create template 2 with the finger image captured next
       
                          scannerCommand(IsPressFingerfps, 0);  // Loop till finger is not removed
                          while(parameterin == 0)
                          {
                            delay(100);
                            scannerCommand(IsPressFingerfps, 0);
                          }    
       
                          Serial.println("Press the same finger again");  
       
                          scannerCommand(IsPressFingerfps, 0);  // Loop till the finger is not pressed
                          while(!(parameterin == 0))
                          {
                            delay(100);
                            scannerCommand(IsPressFingerfps, 0);
                          }
    
                          scannerCommand(CaptureFingerfps, 1);  // Capture finger for 3rd template
                          bret = ack;                            // ack = true if capture was successful
       
                          if(bret != false)
                          {
                                     Serial.println("Remove finger");
                                     scannerCommand(Enroll3fps, 0);  // Create template 3 for the finger and merge it all to create the final template
                                     iret = ack;                     // ack is true if the final template creation was successful
                                     
                                     if(iret == true)
                                     {
                                        Serial.println("Enrolling Successful");   // Print on serial0 that enrolling was successful
                                     }
                                     else
                                     {
                                        Serial.print("Enrolling Failed");
                                     }
                                 
                          }
                          else Serial.println("Failed to capture third finger");
               }
               else Serial.println("Failed to capture second finger");

     }
     else Serial.println("Failed to capture first finger");   
          
}


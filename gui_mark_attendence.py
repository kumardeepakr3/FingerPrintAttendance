#--------------------------------------------------------------------------------------------------------
#FOLLOWING ARE THE PREREQUISITES BEFORE RUNNING THE CODE
#--------------------------------------------------------------------------------------------------------
#1.CREATE DATABASE "COURSES" HAVING TABLE "name_of_courses" attributes defined in code
#2.CREATE DATABASE "python" HAVING TABLE "LOGIN" ATTRIBUTES DEFINED IN CODE
#3.INFO CONTAING STUDENTS LIST MUST BE AVAILABLE BEFOREHAND IN .TXT FORMAT
#4.USERNAME AND PASSWORD OF SQL USER MUST BE REPLACED IN THE CODE
#--------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------
#FOLLOWING ARE LIMITATIONS OF THIS CODE UNTIL NOW
#--------------------------------------------------------------------------------------------------------
#1.THE GUI-WINDOW DOES NOT CLOSE AUTOMATICALLY
#2.THE FINGER_ID IS RECEIVED BUT DUE TO SOME PROBLEMS IN BLUETOOTH-LIBRARY SOMETIMES IT LEADS TO FAILURE
#3.CODE IS INCOMPLETE FOR TWO SECTIONS WHICH WILL BE COMPLETED SHORTLY:
#			(I)RUNNING QUERIES
#			(II)UPDATING PREVIOUS DATA SUCH AS ADD NEW STUDENT AND MARK MISSED ATTENDANCE
#--------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------
#CODE STARTS HERE
#--------------------------------------------------------------------------------------------------------



import tkMessageBox
import Tkinter
from Tkinter import *
import serial
import MySQLdb
import time

#top = Tkinter.Tk()

#SETTING VARIABLE AS GLOBAL VARIABLE AND INITIALLY GIVING SOME RANDOM VALUES
new_user="xyz"
new_pwd="123"
E3="a"
E4="b"
E5="b"
E6="b"
E7="b"
E8="b"



	# Open database connection
db = MySQLdb.connect("localhost","root","nanotech","python" )

	# prepare a cursor object using cursor() method
cursor = db.cursor()

	# Prepare SQL query to INSERT a record into the database.
sql = "SELECT * FROM LOGIN"

	   # Execute the SQL command
cursor.execute(sql)
	   # Fetch all the rows in a list of lists.
results = cursor.fetchall()
#GETTING USERNAME AND PASSWORD FROM INPUT AND PUT THEM IN THESE VARIABLE FOR VERIFYING WHETHER IT IS COORECT OR NOT
for row in results:
      user = row[0]
      password = row[1]
	      #print "user=%s,password=%s" % (user, password)

db.close()

#ENROLLING NEW STUDENTS
def enroll_new_students(student_list):
	#call bluetooth function reveiving code. assume data received in finger_id variable
	finger_id=200
	with open("%s" % student_list, "r") as src:
		with open("/home/priyaranjan/project_summer/studentlist1.txt", "w") as dest:
			for line in src:
				dest.write('%s\t%s\n' % (line.rstrip('\n'),finger_id))
				finger_id=finger_id+1

	dest.close()
	src.close()


#GETTING COURSE NAME AND NUMBER AND FILE PATH CONTAINING STUDENTS LIST FOR CREATING A DATABASE OF THAT COURSE
def new_course():
	window2 = Toplevel()
	window2.geometry('500x250')

	global E5
	global E6
	global E7

	L5 = Label(window2,text="Course Name")
	L5.pack(fill=BOTH, expand=False)

	E5 = Entry(window2, bd =5)
	E5.pack(fill=BOTH, expand=True)

	L6 = Label(window2, text="Course Number")
	L6.pack( fill=BOTH, expand=True)

	E6 = Entry(window2, bd =5)
	E6.pack(fill=BOTH, expand=True)

	L7 = Label(window2, text="File Path")
	L7.pack( fill=BOTH, expand=True)

	E7 = Entry(window2, bd =5)
	E7.pack(fill=BOTH, expand=True)

	B8 = Button(window2,borderwidth=4, text="Create", width=10, pady=8, command= new_course1)
	B8.pack(side=BOTTOM)





	
#CREATING THE TABLES OF EACH STUDENT AND EACH DAY OF THE COURSE AND UDATING THEM WITH STUDENT'S ATTENDANCE
def new_course1():

	course_name=Entry.get(E5)
	course_no=Entry.get(E6)
	student_list=Entry.get(E7)

 	#creating databases in the name of course number
	con = MySQLdb.connect(host="localhost", user="root",passwd="nanotech")
	cur = con.cursor()
	sql="create database %s;" % course_no
	cur.execute(sql)
	
	db = MySQLdb.connect("localhost","root","nanotech", "%s" % course_no)
	cursor=db.cursor()
	sql2 = "CREATE TABLE DATE_AND_DAY (DATES CHAR(20), DAY CHAR(4))"
	cursor.execute(sql2)
	db.commit()
	db.close()



 	#inserting courses name and number in the database of "COURSES"
	db = MySQLdb.connect("localhost","root","nanotech", "COURSES" )

	cursor = db.cursor()

	cursor.execute('INSERT INTO name_of_courses (NAME_OF_COURSE, COURSE_NO) VALUES ("%s","%s")' % (course_name,course_no))

	db.commit()
	db.close()


 	#creating tables and inserting student info to one of the courses(databases)	
	db = MySQLdb.connect("localhost","root","nanotech", "%s" % course_no) 

	cursor = db.cursor()

	#FINGER ID HAS TO BE CHANGED AS REQUIRED	 
	sql1 = "CREATE TABLE STUDENTS_LIST (STUDENT CHAR(100), ROLL CHAR (10), SECTION CHAR(5), DEPARTMENT CHAR(100),FINGER_ID INT(20),PRIMARY KEY(FINGER_ID))" 
	cursor.execute(sql1)

	enroll_new_students(student_list)


	with open('/home/priyaranjan/project_summer/studentlist1.txt', "r") as student_info:
		lines = student_info.readlines()

	for line in lines:
	    # Split the line on whitespace
	    data = line.split()
	    student = data[0]
	    roll= data[1]
	    sec= data[2]
	    dept=data[3]
	    fingerId=data[4]

	    cursor.execute('INSERT INTO STUDENTS_LIST (STUDENT, ROLL, SECTION, DEPARTMENT, FINGER_ID) VALUES ("%s", "%s", "%s", "%s","%s")' % (student,roll,sec,dept,fingerId))
	    

	query_select= "SELECT * FROM STUDENTS_LIST"
	cursor.execute(query_select)

	results = cursor.fetchall()

	for row in results:
		roll_no = "Y" + row[1]
		query_create_table = "CREATE TABLE %s (DATES CHAR(50),DAY CHAR(20), PRESENTorABSENT INT(1),PRIMARY KEY(DAY) )" % roll_no
		cursor.execute(query_create_table) 

	

	db.commit()

	db.close()
	
#FOR CHANGING THE USERNAME AND PASSWORD
def changepwd():
	window1 = Toplevel()
	window1.geometry('500x250')
	
	#label = Label(window1)
	global E3
	global E4

	L3 = Label(window1,text="New User Name")
	L3.pack(fill=BOTH, expand=False)

	E3 = Entry(window1, bd =5)
	E3.pack()
	E3.focus_set()

	L4 = Label(window1, text="New Password")
	L4.pack( fill=BOTH, expand=True)

	E4 = Entry(window1, bd =5,show="*")
	E4.pack()
	E4.focus_set()
	
	B7 = Button(window1,borderwidth=4, text="Reset", width=10, pady=8, command=changepwd2)
	B7.pack(side=BOTTOM)

#EXTENSION OF changepwd()
def changepwd2():
	global new_user
	global new_pwd
	

	new_user=Entry.get(E3)
	print "%s" % (new_user)
	new_pwd=Entry.get(E4)
	print "%s" % (new_pwd)

	changepwd3()

#EXTENSION OF changepwd2()
def changepwd3():
	db = MySQLdb.connect("localhost","root","nanotech","python" )

		# prepare a cursor object using cursor() method
	cursor = db.cursor()
	loginid="1"

	sql = 'UPDATE LOGIN SET NAME = %s, PASSWORD = %s WHERE ID = %s'
	cursor.execute(sql, (new_user, new_pwd, loginid))

	db.commit()



	results = cursor.fetchall()
	for row in results:
	      user = row[0]
	      password = row[1]
	      print "user=%s,password=%s" % (user, password)

	db.close()

#UPDATING TABLES BY MARKING ATTENDANCE
def update_tables(c_no1,strrec,table_name1):

	db = MySQLdb.connect("localhost","root","nanotech","%s" % c_no1)
	cursor=db.cursor()

	#"select ROLL from STUDENTS_LIST where FINGER_ID=%s)" 
	sql= "SELECT ROLL FROM STUDENTS_LIST WHERE FINGER_ID=%s" % strrec
	cursor.execute(sql)

	results= cursor.fetchall()
	for row in results:
		roll_no = row[0]
		roll_no_table= "Y" + roll_no


	#sql1 = 'UPDATE %s SET PRESENTorABSENT = 1 WHERE ROLL_NO = "%s"'
	#cursor.execute(sql1, (table_name1,roll_no))

	cursor.execute('UPDATE %s SET PRESENTorABSENT = 1 WHERE ROLL_NO = "%s"' % (table_name1,roll_no))

	#sql2 = 'UPDATE %s SET PRESENTorABSENT = 1 WHERE  DAY= "%s"'
	cursor.execute('UPDATE %s SET PRESENTorABSENT = 1 WHERE  DAY= "%s"' % (roll_no_table, table_name1))

	db.commit()
	db.close()


	
#FUNCTION FOR RECEIVING THE FINGER ID FROM BLUETOOTH MODULE AND CALLING FUNCTION update_tables 
def bluetooth1(c_no,table_name):
	#timeout=None
	ser = serial.Serial("/dev/rfcomm1", baudrate=9600,timeout=None)
	time.sleep(1)

	receive_str = ''
	
	ser.write("1000") #command and parameter to be sent (This one is only for marking attendence)
	#timeout=None
	for var1 in range(3):
		print "\nloop started"
		receive_str = receive_str + ser.read()
		print "\nreceived"
		time.sleep(0.01)  #Read the 3 digit parameter in string receive_str

	print "\nloop ends"
	strrec = int(receive_str) #string to int. strrec is the unique student ID passed
		
	print strrec
	print "\nanswer printed"

	ser.close()
       
	
	table_name1 = table_name
	c_no1 = c_no
	#print strrec
	update_tables(c_no1,strrec,table_name1)




#CREATING DATE TABLES CONTAINING EACH DATE CLASS WAS TAKEN AND KEEPS TRACK OF NUMBER OF CLASSES TILL DATE
def create_date_table(c_no):
	c_num = c_no

	today_date= Entry.get(E8)

	db = MySQLdb.connect("localhost","root","nanotech","%s" % c_no)
	cursor=db.cursor()
	sql = "select count(*) from DATE_AND_DAY"
	cursor.execute(sql)
	results = cursor.fetchall()
	for row in results:
	      x = row[0]
	      day=x+1

	
	cursor.execute('INSERT INTO DATE_AND_DAY (DATES, DAY) VALUES ("%s", "%s")' % (today_date,day))
	db.commit()
	db.close()

	
	db = MySQLdb.connect("localhost","root","nanotech", "%s" % c_no) 
	days=str(day)
	cursor = db.cursor()
	table_name = "D" + days
	sql1 = "CREATE TABLE %s ( ROLL_NO CHAR (10), PRESENTorABSENT int(1))" % table_name
	cursor.execute(sql1)

	

	
	sql3= "select * from STUDENTS_LIST"
	cursor.execute(sql3)
	results1 = cursor.fetchall()
	for rows in results1:
		y = rows[1]
		roll = "Y" + "%s" % y
		cursor.execute('INSERT INTO %s (DATES, DAY, PRESENTorABSENT) VALUES ("%s","%s",0)' % (roll,today_date, table_name))
		cursor.execute('INSERT INTO %s (ROLL_NO, PRESENTorABSENT) VALUES ("%s",0)' % (table_name,y))




	db.commit()


	db.close()

	bluetooth1(c_num,table_name)
	
#INSERT TODAY'S DATE FOR MARKING ATTENDANCE
def enter_date(c_no):
	window4=Toplevel()
	window4.geometry('500x250')
	global E8


	L8 = Label(window4,text="Enter Today's Date(yyyy-mm-dd)")
	L8.pack( expand=False)

	E8 = Entry(window4, bd =5)
	E8.pack( expand=False)

	B8 = Button(window4,borderwidth=4, text="Next", width=10, pady=8, command=lambda c_no=c_no :create_date_table(c_no))
	B8.pack()

#cHOOSE COURSE WHOSE ATTENDANCE HAS TO BE MARKED
def choose_course():
	window3=Toplevel()
	window3.geometry('500x250')

	message1 = StringVar()
	label1 = Message( window3, textvariable=message1,aspect=1000)

	message1.set("Choose from the following courses:")
	label1.pack()
	

	import MySQLdb

	db = MySQLdb.connect("localhost","root","nanotech","COURSES" )
	cursor = db.cursor()

	#sql = "select count(*) from information_schema.tables where table_schema='COURSES'"

	sql = "select count(*) from name_of_courses"

	cursor.execute(sql)
		 
	results = cursor.fetchall()
	for row in results:
	      x = row[0]
	      no_of_courses=x
	      #print no_of_courses

	#R = [0 for i in range(no_of_courses)]
	C = [0 for j in range(no_of_courses)]

	sql0 = "select * from name_of_courses"
	cursor.execute(sql0)

	results1= cursor.fetchall()

	j=0;


	for row in results1:
		C[j]=row[1]
		#print C[j]
		j=j+1

	for i in range(no_of_courses):
		#var1 = StringVar()
		#msg=StringVar()
		#msg.set("%s" % C[i])
		#R = Button(window3, textvariable=msg, command=fn(C[i]))
		a=C[i]
		R = Button(window3, text="%s" % a, command=lambda a=a: enter_date(a))
		R.pack()


	label2=Label(window3)
	label2.pack()
	      #password = row[1]
		      #print "user=%s,password=%s" % (user, password)

	db.close()

#TO BE UPDATED AFTER RUNNING BLUETOOTH SUCCESSFULLY
def add_new_student():
	window6=Toplevel()
	window6.geometry('500x250')
	L9 = Label(window6,text="Name")
	L9.pack(fill=BOTH, expand=False)

	E9 = Entry(window6, bd =5)
	E9.pack( expand=True)

	L10 = Label(window6,text="Roll No")
	L10.pack(fill=BOTH, expand=False)

	E10 = Entry(window6, bd =5)
	E10.pack( expand=True)

	L11 = Label(window6,text="Section")
	L11.pack(fill=BOTH, expand=False)

	E11 = Entry(window6, bd =5)
	E11.pack( expand=True)

	L12 = Label(window6,text="Department")
	L12.pack(fill=BOTH, expand=False)

	E12 = Entry(window6, bd =5)
	E12.pack( expand=True)

	B11 = Button(window6,borderwidth=4, text="Next", width=20, pady=8)
	B11.pack() 


#TO BE UPDATED AFTER RUNNING BLUETOOTH SUCCESSFULLY
def mark_missed_attendance():
	window7=Toplevel()
	window7.geometry('500x250')
	L13 = Label(window7,text="Roll No")
	L13.pack(expand=False)

	E13 = Entry(window7, bd =5)
	E13.pack()

	B12 = Button(window7,borderwidth=4, text="Next", width=10, pady=8)
	B12.pack()

#FUNCTION FOR UPDATING DATA(FOR ADDING NEW STUDENT AND MARKING MISSED ATTENDANCE)
def update_data():
	window5=Toplevel()
	window5.geometry('500x250')
	B9 = Button(window5,borderwidth=4, text="Add new student", width=30, pady=8, command=add_new_student)
	B9.pack()
	B10 = Button(window5,borderwidth=4, text="Mark missed attendance of a student", width=30, pady=8, command=mark_missed_attendance)
	B10.pack()

#FUNCTION FOR RUNNING FOLLOWING QUERIES
def run_query():
	window8 = Toplevel()
	window8.geometry('500x250')
	B13 = Button(window8,borderwidth=4, text="Overall Attendance For a Particular Day", width=60, pady=8, command=Q1)
	B13.pack()
	B14 = Button(window8,borderwidth=4, text="Attendence for a single student till date", width=60, pady=8, command=Q2)
	B14.pack()
	B15 = Button(window8,borderwidth=4, text="Names of all students whose attendance falls b/w X(%) and Y(%)", width=60, pady=8, command=Q3)
	B15.pack()
	B16 = Button(window8,borderwidth=4, text="Overall attendance percent throughout the semester for all the students", width=60, pady=8,command=Q4)
	B16.pack()

def Q1():
	print "not complete yet"


def Q2():
	print "not complete yet"

def Q3():
	print "not complete yet"

def Q4():
	print "not complete yet"

#NEXT WINDOW IN WHICH ALL THE MAIN MENU OPTIONS ARE DISPLAYED
def new_window():
        #self.count += 1
        #id = "New window #%s" % self.count
        #root.destroy()
    	window = Toplevel()
        #window.title('FingerPrint Attendance ')
        window.geometry('500x250')
       # label = Label(window)
        B2 = Button(window,borderwidth=4, text="New Course", width=20, pady=8, command=new_course)
        B2.pack()
        B3 = Button(window,borderwidth=4, text="Update Data", width=20, pady=8, command=update_data)
        B3.pack()
        B4 = Button(window,borderwidth=4, text="Mark Attendance for a Course", width=20, pady=8, command=choose_course)
        B4.pack()
        B5 = Button(window,borderwidth=4, text="Run Query", width=20, pady=8,command=run_query)
        B5.pack()

        B6 = Button(window,borderwidth=4, text="Change Password or User Name", width=20, pady=8, command= changepwd)
        B6.pack()

        #label.pack(side="top", fill="both", padx=300, pady=200)

#FUNCTION FOR CHECKING THE CORRECT USERNAME AND PASSWORD
def verifypwd():
	if user==E1.get() and password==E2.get():
		new_window()
		#root.destroy()
	else:
		var = StringVar()
		label = Message( frame, textvariable=var, relief=RAISED )
		var.set("Invalid User Name or Password!!")
		label.pack()

root = Tk()
frame = Frame(root)
frame.pack()




#tkMessageBox.showinfo("FingerPrint Attendance system", "Welcome!")

#fill=tk.BOTH, expand=True


#MAIN WINDOW FOR LOGIN IN DATABASE
root.title("FingerPrint Attendance system")
root.geometry('500x250')

L1 = Label(frame,text="User Name")
L1.pack(fill=BOTH, expand=False)

E1 = Entry(frame, bd =5)
E1.pack(fill=BOTH, expand=True)

L2 = Label(frame, text="Password")
L2.pack( fill=BOTH, expand=True)

E2 = Entry(frame, bd =5,show="*")
E2.pack(fill=BOTH, expand=True)

B1 = Button(frame,borderwidth=4, text="Login", width=10, pady=8, command=verifypwd)
B1.pack(side=BOTTOM)

frame.mainloop()

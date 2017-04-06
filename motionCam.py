#!/usr/bin/python
# pir_1.py
# Detect movement using a PIR module

# Import required Python libraries
import RPi.GPIO as GPIO
import time
import datetime
from picamera import PiCamera
from time import sleep
from picamera import PiCamera, Color
import getpass      #Password hider
import pickle       #used to store the passwords in a file
#Used for push notifications
import pycurl, json 
from StringIO import StringIO

#Email
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

camera = PiCamera()
i = datetime.datetime.now()
vidCam = 0

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_PIR = 4

# Set pin as input
GPIO.setwarnings(False)
GPIO.setup(GPIO_PIR,GPIO.IN)      # Echo

#___________________Push Notification Setup__________________

#addyout InstaPush Application ID
appID = "Enter your appID"

#add your Instapush Application Secret
appSecret = "Enter your appSecret"
pushEvent = "MotionDetected"
pushMessage = "Motion Detected"

#use this to capture the response from out push API call
buffer = StringIO()

#use Curl to post to the InstaPush API
c = pycurl.Curl()
#set Instapush API URL
c.setopt(c.URL, 'https://api.instapush.im/v1/post')

#setup custom headers for authentication variables and content type
c.setopt(c.HTTPHEADER, ['x-instapush-appid: ' + appID,
			'x-instapush-appsecret: ' + appSecret,
			'Content-Type: application/json'])

#create a dict structure for the JSON data to post
json_fields = {}

#setup JSON values 
json_fields['event']=pushEvent
json_fields['trackers'] = {}
json_fields['trackers']['message']=pushMessage
#print (json_fields)
postfields = json.dumps(json_fields)

#make sure to sent the JSON with post
c.setopt(c.POSTFIELDS, postfields)

#set this so we can capture the response in our buffer
c.setopt(c.WRITEFUNCTION, buffer.write)


#________________Push Notification Setup End________________

#___________________Push Notification_______________________
def push():
  #send the push request
  c.perform()

  #print the response
  print"Push Notification Sent"
  #print(body)

  #reset the buffer
  buffer.truncate(0)
  buffer.seek(0)

#___________________Push Notification End_____________________
  
#___________________Email Code Starts________________________
def email(password, vidCam):
  #Settings variables for the messages 
  fromaddr = "your email@gmail.com"
  toaddr = "your email"

  msg = MIMEMultipart()

  msg['From'] = fromaddr
  msg['To'] = toaddr
  msg['Subject'] = "Test Email"

  body = "Motion has been sensed by you Pi Cam. Attached is evidence of what caused the motion."

  msg.attach(MIMEText(body, 'plain'))

  if vidCam==1:
    filename = "video1.h264"
    attachment = open("Enter file path /video.h264", "rb")
  else:
    filename = "image1.jpg"
    attachment = open("Enter file path /image1.jpg", "rb")

  part = MIMEBase('application', 'octet-stream')
  part.set_payload((attachment).read())
  encoders.encode_base64(part)
  part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

  msg.attach(part)

  #Log in details and server 
  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.starttls()
  server.login("your email@gmail.com", password)


  text = msg.as_string()
  server.sendmail(fromaddr, toaddr, text)

  server.quit()

#___________________Email Code Ends ________________________


#___________________Take Picture Code Starts _____________________
def takepic():
  camera.rotation = 180
  camera.start_preview()
  camera.annotate_text = time.strftime("%a, %d, %b, %Y %H:%M:%S")
  sleep(5)
  camera.capture('Enter file path/image1.jpg')
  camera.annotate_text = time.strftime("%a, %d, %b, %Y %H:%M:%S")
  camera.stop_preview()

#___________________Take Picture Code Ends________________________


#___________________Take Video Code Starts________________________
def takevid():
  camera.rotation = 180
  camera.start_preview()
  camera.annotate_text = time.strftime("%a, %d, %b, %Y %H:%M:%S")
  camera.annotate_foreground = Color('yellow')
  camera.start_recording('Enter file path/video.h264')
  sleep(5)
  camera.stop_recording()
  camera.stop_preview()

#___________________Take Video Code Ends________________________


#_____________________Code Starts here________________________

print "PIR Module Test (CTRL-C to exit)"

#___________________Log In Code + Motion!!!!________________________


users = pickle.load(open("users.pickle", "rb"))


with open('users.pickle', 'rb') as handle:
    b = pickle.load(handle)

print users == b 

    
loginAtempts = 0

status = ""

def displayMainMenu():
    
    status = raw_input("Are you a registered user? y/n? Press q to quit: ")
    if status == "y":
        existingUser()
    elif status == "n": #ADD IN CODE THAT ONLY ALLOWS A CURRENT PERSON TO ADD NEW USER
        newUser()
    return status

def newUser():
    createLogin = raw_input("Create Username: ")

    if createLogin in users:    #check if login name exist in the dictionary
        print "Username already exist!\n"
    else:
        createPassw = raw_input("Create password: ")
        users[createLogin] = createPassw 	#add login and password
        with open('users.pickle','wb') as handle:
            pickle.dump(users, handle)
        print("\nUser created!\n")
        existingUser()

def existingUser():
    login = raw_input("Enter Username: ")
    passw = getpass.getpass("Enter Password: ")

#Check to see if user exists and the username matches the password
    if login in users and users[login] == passw:
        print "\nLogin Successful\n"

        #Enter email password without having to store it
        password = getpass.getpass(prompt= "Enter email password:")

        camStatus = raw_input("Photo or Video? P = Photo, V = Video:  ")
        if camStatus == "P" or camStatus == "p":
          vidCam = 0
        if camStatus == "V" or camStatus == "v": #ADD IN CODE THAT ONLY ALLOWS A CURRENT PERSON TO ADD NEW USER
          vidCam = 1
        else:
          vidCam = 0
        
        
        Current_State  = 0
        Previous_State = 0
        try:

          print "Waiting for PIR to settle ..."

          # Loop until PIR output is 0
          while GPIO.input(GPIO_PIR)==1:
            Current_State  = 0    

          print "  Ready"
          
    
          # Loop until users quits with CTRL-C
          while True :
   
            # Read PIR state
            Current_State = GPIO.input(GPIO_PIR)
           
            if Current_State==1 and Previous_State==0:
                print "Motion Detected", time.strftime("%a, %d, %b, %Y %H:%M:%S")
                if vidCam==1:
                  takevid()
                else:
                  takepic()
                  
                push()
                email(password, vidCam)
              # Record previous state
              	Previous_State=1
              	
            elif Current_State==0 and Previous_State==1:
              # PIR has returned to ready state
              print "  Ready"
              Previous_State=0
      
            # Wait for 10 milliseconds
            time.sleep(0.01)      
      

        except KeyboardInterrupt:
          print " Log Out" 
          # Reset GPIO settings
          c.close()
          GPIO.cleanup()
        
    else:
        print"\nUsername or password incorrect!\n"


while status != "q":

    status = displayMainMenu()
    
#___________________Log In Code + Motion Ends ________________________
# Authors: Stephanie Beech and Luke Fenton

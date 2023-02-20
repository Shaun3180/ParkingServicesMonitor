#!/usr/bin/env python3

import cv2
import time
import subprocess
import paramiko
import datetime
import logging

from picamera2 import Picamera2

# for logging
logging.basicConfig(filename='/home/pi/apps/fcmonitor/parking-services-monitor.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

# SFTP creds
sftphost = ""
sftpuser = ""
sftppass = ""
sftpremotepath = ""

# Twilio API creds
sendSMS = True
account_sid = ""
auth_token = ""
to_number = '+'
from_number = '+'

pathToScriptDirectory = ''

# Grab images as numpy arrays and leave everything else to OpenCV
car_detector = cv2.CascadeClassifier(pathToScriptDirectory + "car-classifier.xml")
#cv2.startWindowThread()

# start Pi Camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# disallow more positive ids than once every 5 seconds
detected_time = 0

# set a counter for debugging purposes
loopCounter = 0

while True:
    
    try:
        
        # Read the next frame
        frame = picam2.capture_array()
        
        # increment/show counter
        loopCounter += 1
        #print(loopCounter)

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect objects in the frame using haar cascade
        objects = car_detector.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=6, minSize=(200, 200))
        
        # Draw a rectangle around matched objects
        for (x, y, w, h) in objects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Check if it has been more than 5 seconds since the last detection
            # since I don't want to be bombarded with text messages
            if len(objects) > 0 and time.time() - detected_time >= 5:
                detected_time = time.time()
                
                # print car found to console
                print('car found!')
                
                # Display the current frame with the rectangle drawn on it
                #cv2.imshow('frame', frame)
                
                # Also save the image if a positive match is found
                image_name = "detectedobject.jpg"
                cv2.imwrite(pathToScriptDirectory + image_name, frame)
                
                # Connect to the SFTP server
                # Modeled after https://stackoverflow.com/questions/3635131/paramikos-sshclient-with-sftp
                #paramiko.util.log_to_file("paramiko.log")

                # Open a transport
                host,port = sftphost,22
                transport = paramiko.Transport((host,port))

                # Auth    
                username,password = sftpuser,sftppass
                transport.connect(None,username,password)

                # Connect
                sftp = paramiko.SFTPClient.from_transport(transport)

                # Upload file
                filepath = sftpremotepath + image_name
                localpath = pathToScriptDirectory + image_name
                sftp.put(localpath,filepath)

                # Close connection
                if sftp: sftp.close()
                if transport: transport.close()
                
                # if we need to also send an mms message 
                if (sendSMS):

                        # The body of the text message
                        message = 'We spotted a FC city vehicle!'

                        # get todays date
                        today = datetime.datetime.now().strftime("%Y-%m-%d%H-%M-%S")

                        # get full url to FTP'd image
                        image = 'https://e1d.f49.myftpupload.com/detectedobject.jpg?dl=' + today

                        #print('link to image: ' + image)

                        # The Twilio API endpoint for sending SMS messages
                        url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'

                        # Use curl to make an HTTP POST request to the Twilio API
                        result = subprocess.run(['curl', '-X', 'POST', url, '-u', f'{account_sid}:{auth_token}',
                                                '--data-urlencode', f'To={to_number}',
                                                '--data-urlencode', f'From={from_number}',
                                                '--data-urlencode', f'Body={message}',
                                                '--data-urlencode', f'MediaUrl={image}'],
                                            stdout=subprocess.PIPE)

                        # Check the response from the Twilio API
                        if result.returncode == 0:
                            print('Text message sent successfully!')
                        else:
                            print('An error occurred while sending the text message.')
                
    except Exception as e:
        #print(e)
        #log it
        logger.error(err)
       
    # Exit on ESC
    if cv2.waitKey(30) == 27:
        break

# Release the video and close the window
cv2.destroyAllWindows()

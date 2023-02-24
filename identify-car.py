#!/usr/bin/env python3

import cv2
import time
import subprocess
import paramiko
import datetime
import logging
import os

from picamera2 import Picamera2

# Set up constants
sftpHost = ""
sftpUser = ""
sftpPass = ""
sftpRemotePath = ""
sendSMS = False
accountSid = ""
authToken = ""
toNumber = "+"
fromNumber = "+"
pathToScriptDirectory = ""

# Configure logging
logging.basicConfig(filename=pathToScriptDirectory + "parking-services-monitor.log", level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

# Grab images as numpy arrays and leave everything else to OpenCV
car_detector = cv2.CascadeClassifier(os.path.join(pathToScriptDirectory, "car-classifier.xml"))

# start Pi Camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# disallow more positive ids than once every 5 seconds
detected_time = 0
loopCounter = 0

try:

    while True:
        
        carDetections = None

        try:

            # get todays date in string format
            today = datetime.datetime.now().strftime("%Y-%m-%d%H-%M-%S")
            
            # Read the next frame
            frame = picam2.capture_array()
            
            # increment/show counter
            loopCounter += 1
            #print(loopCounter)

            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect cars in the frame using haar cascade
            carDetections = car_detector.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=6, minSize=(200, 200))

        except Exception as detectionError:
            #print(e)
            logger.exception(detectionError)
        
            # Draw a rectangle around matched carDetections
            for (x, y, w, h) in carDetections:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Check if it has been more than 5 seconds since the last detection
                # since I don't want to be bombarded with text messages
                if len(carDetections) > 0 and time.time() - detected_time >= 5:
                    detected_time = time.time()
                    
                    # print car found to console
                    #print('car found!')
                    logger.debug(f"Car detected at {today}")
                    
                    # Display the current frame with the rectangle drawn on it
                    #cv2.imshow('frame', frame)
                    
                    # Also save the image if a positive match is found
                    detectedObjectImage = "detectedobject.jpg"
                    cv2.imwrite(pathToScriptDirectory + detectedObjectImage, frame)
                    
                    # Connect to the SFTP server
                    try:
                        with paramiko.Transport((sftpHost, 22)) as transport:
                            transport.connect(username=sftpUser, password=sftpPass)
                            with paramiko.SFTPClient.from_transport(transport) as sftp:
                                sftp.put(pathToScriptDirectory + detectedObjectImage, sftpRemotePath + detectedObjectImage)
                                logger.debug(f"Uploaded {detectedObjectImage} to {sftpHost}")
                    except Exception as sftpError:
                        logger.exception(sftpError)
                        # If the SFTP connection fails, save the image with a datestamp in its file name
                        cv2.imwrite(pathToScriptDirectory + today, frame)
                        logger.debug(f"Due to SFTP error, image saved locally as {filename}")
                    
                    # if we need to also send an mms message 
                    if (sendSMS):

                            try:

                                # The body of the text message
                                message = "We spotted a FC city vehicle!"

                                # get full url to FTP'd image
                                image = f"https://e1d.f49.myftpupload.com/detectedobject.jpg?dl={today}"

                                # The Twilio API endpoint for sending SMS messages
                                url = f"https://api.twilio.com/2010-04-01/Accounts/{accountSid}/Messages.json"

                                # Use curl to make an HTTP POST request to the Twilio API
                                result = subprocess.run(['curl', '-X', 'POST', url, '-u', f'{accountSid}:{authToken}',
                                                        '--data-urlencode', f'To={toNumber}',
                                                        '--data-urlencode', f'From={fromNumber}',
                                                        '--data-urlencode', f'Body={message}',
                                                        '--data-urlencode', f'MediaUrl={image}'],
                                                    stdout=subprocess.PIPE)

                                # Check the response from the Twilio API
                                if result.returncode == 0:
                                    print("Text message sent successfully!")
                                else:
                                    print("An error occurred while sending the text message.")
                            except Exception as smsError:
                                logger.exception(smsError)    
        
        
        # Exit on ESC
        if cv2.waitKey(30) == 27:
            break

except Exception as otherError:
    logger.exception(otherError)   

# Release the video and close the window
cv2.destroyAllWindows()

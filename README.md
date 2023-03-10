

# Raspberry Pi Parking Services Monitor

This project's goal is to avoid parking tickets.  The general idea is to use a Pi camera / Haar cascade to attempt to recognize a passing City of Fort Collins parking services vehicle so I don't  have to move my car quite as frequently (i.e., to park in one spot for longer without worrying about parking tickets).  As I park in a 2 hour parking zone, I want to be able to park for as long as I can without having to move my car unnecessarily.   Therefore, once a parking services vehicle drives by, the Pi's job is to try and recognize their distinct vehicle and text an image of it to me for verification purposes, at which point I know that I will need to move my vehicle 2 hours later (since as far as parking services knows, I had just parked there).

Note: Use at your own risk - this is my first foray with Python, FWIW... 

![Positive Match](https://raw.githubusercontent.com/Shaun3180/ParkingServicesMonitor/main/detectedobject.jpg)

![Twilio Text Message](https://github.com/Shaun3180/ParkingServicesMonitor/blob/main/IMG_E4FC4E5CE2D0-1.jpeg?raw=true)

## Requirements

* A **Raspberry Pi**.  I used https://smile.amazon.com/gp/product/B07BDRD3LP/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1, which I realize is an older model, but I already had it on hand, and that is one reason I'm using a Haar cascade and not something more processor intensive, like TensorFlow. 
* A **USB C Power Bank**.  I used https://smile.amazon.com/dp/B07P5ZP943?ref=ppx_yo2ov_dt_b_product_details&th=1
* A **camera module**.  I used https://smile.amazon.com/dp/B073183KYK?psc=1&ref=ppx_yo2ov_dt_b_product_details
* A **WiFi connection** from wherever you park
* **OpenCV** 3.0.0 and **Python3**

## Overview of Goals

* Once powered on, the Pi should automatically connect to Wifi.  Since Wifi is spotty is where i park, the Pi will start polling a separate app I wrote every 5 minutes.  If a ping is unsuccessful, I will be sent a text alert using Twilio
* Once powered on, the Pi camera will continuously monitor the road using the [identify-car.py](https://github.com/Shaun3180/ParkingServicesMonitor/blob/main/identify-car.py "identify-car.py") python script.
* When a passing vehicle matches a trained Haar cascade, identifying a city vehicle, a still of the positive match will be saved/sent via FTP to a server I have access to.
* Using Twilio, that FTP'd image will be sent to me for verification purposes

## General Steps To Recreate

* Install Raspberry Pi OS using Raspberry Pi Imager: [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)
	* Note: it's very helpful to click the gear icon in the Imager settings to specify your WiFi settings that you want the pi to connect to in advance, as well as to enable SSH
* Optional: I only have headless access to my Pi via my Mac.  Here are good directions on how to get that going using Screen Sharing in OS X: https://raspberrypi.stackexchange.com/questions/59605/access-to-raspberry-pi-vnc-session-from-mac-os-x#answer-79626. 
* Install OpenCV (for handling haar cascades): pip install opencv-python
* Install Twilio (for sending me a text) using: pip install twilio
* Install Paramiko (for uploading files using SFTP) using: pip install paramiko.  While attempting to install paramiko, I received the following error: "Failed to build wheel for bcrypt", which I solved using sudo pip install -U "bcrypt<4.0.0", as per https://github.com/adriankumpf/teslamate/discussions/2881
* Edited crontab -e to make sure my identify-car python script runs on boot (see screenshot below) and logs errors to a log.log file: @reboot python /path/to/file.py >> /path/to/log.log 2>&1
* Most importantly, I used the free Windows app, "[CASCADE TRAINER GUI](https://amin-ahmadi.com/cascade-trainer-gui/)" in order to train my model.  You can use the following python script to obtain a sample 30 minute video from which you can create still images to create your Haar classifier:

save-video.py:

    import time
    
    from picamera2.encoders import H264Encoder
    from picamera2 import Picamera2
    
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
    picam2.configure(video_config)
    encoder = H264Encoder(bitrate=10000000)
    output = "/home/pi/apps/save-video/footage.h264"
    picam2.start_recording(encoder, output)
    time.sleep(1800)
    picam2.stop_recording()

sample crontab-e:

![enter image description here](https://github.com/Shaun3180/ParkingServicesMonitor/blob/main/crontab-example.jpg?raw=true)

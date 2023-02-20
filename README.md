
# Raspberry Pi Parking Services Monitor

This project's goal is to avoid parking tickets.  The general idea is to use a Pi camera / Haar cascade to attempt to recognize a passing City of Fort Collins parking services vehicle so I don't  have to move my car quite as frequently (i.e., to park in one spot for longer without worrying about parking tickets).  As I park in a 2 hour parking zone, I want to be able to park for as long as I can without having to move my car unnecessarily.   Therefore, once a parking services vehicle drives by, the Pi's job is to try and recognize their distinct vehicle and text an image of it to me for verification purposes, at which point I know that I will need to move my vehicle 2 hours later (since as far as parking services knows, I had just parked there).

Note: this is my first foray with Python, FWIW... 

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
* Once powered on, the Pi camera will continuously monitor the road.
* When a passing vehicle matches a trained Haar cascade, identifying a city vehicle, a still of the positive match will be saved sent via FTP to a server I have access to.
* Using Twilio, that FTP'd image will be sent to me for verification purposes

## General Steps To Recreate

* Install Raspberry Pi OS using Raspberry Pi Imager: [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)
	* Note: it's very helpful to click the gear icon in the Imager settings to specify your WiFi settings that you want the pi to connect to in advance, as well as to enable SSH
* Optional: I only have headless access to my Pi via my Mac.  Here are good directions on how to get that going using Screen Sharing in OS X: https://raspberrypi.stackexchange.com/questions/59605/access-to-raspberry-pi-vnc-session-from-mac-os-x#answer-79626. 
* Install OpenCV (for handling haar cascades): pip install opencv-python
* Install Twilio (for sending me a text) using: pip install twilio
* Install Paramiko (for uploading files using SFTP) using: pip install paramiko.  While attempting to install paramiko, I received the following error: "Failed to build wheel for bcrypt", which I solved using sudo pip install -U "bcrypt<4.0.0", as per https://github.com/adriankumpf/teslamate/discussions/2881
* As per https://raspberrypi-guide.github.io/programming/run-script-on-boot#using-rclocal, edited crontab -e to make sure my identify-car python script runs on boot and logs errors to a log.log file: @reboot python /path/to/file.py >> /path/to/log.log 2>&1
* Most importantly, I used the free Windows app, "[CASCADE TRAINER GUI](https://amin-ahmadi.com/cascade-trainer-gui/)" in order to train a model using about 70 positive and negative images.  Ideally I'd like to obtain a lot more than that (to reduce false positives), but it's good enough for now, given I am able to verify each image and I park on a lightly-trafficked road.

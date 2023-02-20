import cv2
import time

# Load the Haar Cascade classifier
classifier = cv2.CascadeClassifier("car-classifier.xml")

# Load either the positive or negative video file, negative1.mov has 292 frames
cap = cv2.VideoCapture('/home/pi/apps/fcmonitor/positive1.mov')

detected_time = 0
loopCounter = 0

# Loop through the frames of the video
while True:
    
    try:
        
        # Read in the current frame
        ret, frame = cap.read()
        
        if not ret:
            break 
    
        # show counter
        loopCounter += 1
        print(loopCounter)

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

       # Detect objects in the frame
        objects = classifier.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=6, minSize=(200, 200))
        
        # Draw a rectangle around the objects
        for (x, y, w, h) in objects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Check if it has been more than 5 seconds since the last detection
            if len(objects) > 0 and time.time() - detected_time >= 5:
                detected_time = time.time()
                
                # car found
                print('car found!')
                
                # Display the current frame with contours drawn on it
                cv2.imshow('frame', frame)
                
                # Save the image if a positive match is found
                cv2.imwrite("detected_object.jpg", frame)
                
    except Exception as e: print(e)

    # Wait for a key press to advance to the next frame
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close the display window
cap.release()
cv2.destroyAllWindows()

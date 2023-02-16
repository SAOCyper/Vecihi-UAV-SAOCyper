#CAMERA DISTANCE
import numpy as np 
import cv2
path_txt = r"C:\CYCLOP\GLADOS\MobileNetSSD_deploy.prototxt.txt"
patf_caffe = r"C:\CYCLOP\GLADOS\MobileNetSSD_deploy.caffemodel"
# Load the pre-trained model
net = cv2.dnn.readNetFromCaffe(path_txt, patf_caffe)

# Capture frame-by-frame from your camera 
cap = cv2.VideoCapture(0)
def detect_object():
    while True:
        # Capture frame-by-frame
        _, image = cap.read()
        focal_length =  640
        # Real height of the person/object 
        object_height = 60
        # Get the width and height of the image
        (h, w) = image.shape[:2]

        # Resize the image to 300x300 for better accuracy
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

        # Pass the blob through the network to detect objects
        net.setInput(blob)
        detections = net.forward()

        # Use the detections to draw boxes around the objects
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            # Filter out weak detections by ensuring the confidence is greater than the minimum confidence
            if confidence > 0.2:
                # Get the x,y coordinates of the object
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                w = endX- startX 
                h = endY - startY
                object_height_pixels = h
                # Calculating distance 
                distance = focal_length * object_height / object_height_pixels 
                print ("Distance (in cm): %d" %distance ) 
                # Draw the box and label on the image
                label = "{}: {:.2f}".format("distance", distance)
                cv2.rectangle(image, (startX, startY), (endX, endY), (0,255,0), 2)
                cv2.putText(image, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)

        # Show the output image
        cv2.imshow("Output", image)
        key = cv2.waitKey(1) & 0xFF

        # If `q` key is pressed, break from the loop
        if key == ord("q"):
            break

    # Release the camera and close any open windows
    cap.release()
    cv2.destroyAllWindows()

def control_servos():
    import time
    import mavlink
    import mavlink.pixhawk
    # Load the classifier for detecting planes
    plane_cascade = cv2.CascadeClassifier('haarcascade_plane.xml')
    # Connect to the Pixhawk using the mavlink library
    pixhawk = mavlink.pixhawk.Pixhawk()
    pixhawk.connect("/dev/ttyACM0")

    # PID controller constants
    KP = 0.01  # Proportional gain
    KI = 0.01  # Integral gain
    KD = 0.01  # Derivative gain

    # PID controller variables
    last_error = 0.0  # Last error
    integral = 0.0  # Integral of the error

    # Function to control the servos using a PID controller
    def move_to_center(x, y):
        global last_error, integral

        # Calculate the error between the current position and the desired position
        error_x = 640/2 - x
        error_y = 480/2 - y

        # Calculate the integral of the error
        integral += error_x + error_y

        # Calculate the derivative of the error
        derivative_x = error_x - last_error[0]
        derivative_y = error_y - last_error[1]
        last_error = (error_x, error_y)

        # Calculate the desired pan and tilt angles based on the PID controller formula
        pan = KP * error_x + KI * integral + KD * derivative_x
        tilt = KP * error_y + KI * integral + KD * derivative_y

        # Send the MAV_CMD_DO_SET_SERVO message to the Pixhawk to move the servos
        pixhawk.mav.command_long_send(
            pixhawk.target_system,
            pixhawk.target_component,
            mavlink.MAV_CMD_DO_SET_SERVO,
            0,
            1,  # Set servo 1 (pan) to the desired angle
            pan,
            2,  # Set servo 2 (tilt) to the desired angle
            tilt,
            0,
            0,
            0,
            0
        )

    # Function to detect the object in the camera and return its coordinates
    def detect_object():
        # Capture a frame from the camera
        ret, frame = cap.read()

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect planes in the frame
        planes = plane_cascade.detectMultiScale(gray, 1.3, 5)

        # If a plane is detected, return its coordinates
        if len(planes) > 0:
            x, y, w, h = planes[0]
            return x + w/2, y + h/2

        # If no plane is detected, return the center of the frame as a default
        return 640/2, 480/2

        # Main loop
    while True:
        # Check if there is an object bounded by a box in the camera
        x, y = detect_object()

        # If the object is not in the center of the frame, move the servos to center it
        if abs(x - 640/2) > 20 or abs(y - 480/2) > 20:
            move_to_center(x, y)

        time.sleep(0.1)



""" import time
import mavlink
import mavlink.pixhawk

# Connect to the Pixhawk using the mavlink library
pixhawk = mavlink.pixhawk.Pixhawk()
pixhawk.connect("/dev/ttyACM0")

# PID controller constants
KP = 0.01  # Proportional gain
KI = 0.01  # Integral gain
KD = 0.01  # Derivative gain

# PID controller variables
last_error = 0.0  # Last error
integral = 0.0  # Integral of the error

# Function to control the servos using a PID controller
def move_to_center(x, y):
  global last_error, integral

  # Calculate the error between the current position and the desired position
  error_x = 640/2 - x
  error_y = 480/2 - y

  # Calculate the integral of the error
  integral += error_x + error_y

  # Calculate the derivative of the error
  derivative_x = error_x - last_error[0]
  derivative_y = error_y - last_error[1]
  last_error = (error_x, error_y)

  # Calculate the desired pan and tilt angles based on the PID controller formula
  pan = KP * error_x + KI * integral + KD * derivative_x
  tilt = KP * error_y + KI * integral + KD * derivative_y

  # Send the MAV_CMD_DO_SET_SERVO message to the Pixhawk to move the servos
  pixhawk.mav.command_long_send(
    pixhawk.target_system,
    pixhawk.target_component,
    mavlink.MAV_CMD_DO_SET_SERVO,
    0,
    1,  # Set servo 1 (pan) to the desired angle
    pan,
    2,  # Set servo 2 (tilt) to the desired angle
    tilt,
    0,
    0,
    0,
    0
  )

# Function to detect the object in the camera and return its coordinates
def detect_object():
  # Implement object detection here using a library like OpenCV
  x = 640/2  # Return the center of the frame as an example
  y = 480/2
  return x, y

# Main loop
while True:
  # Check if there is an object bounded by a box in the camera
  x, y = detect_object()

  # If the object is not in the center of the frame, move the servos to center it
  if abs(x - 640/2) > 20 or abs(y - 480/2) > 20:
    move_to_center(x, y)

  time.sleep(0.1) """

detect_object()

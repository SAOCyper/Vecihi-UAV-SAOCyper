from pymavlink import mavutil

import pymavlink
import time
from pymavlink import mavutil
frame_width = 200
frame_height = 200

# Connect to the Mavlink Server
mav = pymavlink.MAVLink(host='localhost', port=5760)

# Connect to the servos
servos = [Servo(port='/dev/servo0'), 
          Servo(port='/dev/servo1')]

# Get the current servo positions
pan_angle, tilt_angle = mav.get_servo_positions()
# pan angle is horizontal, tilt angle is vertical

# Set the object detection object bounding box
x1, y1, x2, y2 = 0, 0, 100, 100

# Calculate the object center coordinates in the bounding box
object_x = (x1 + x2) / 2
object_y = (y1 + y2) / 2

# Calculate the desired pan and tilt angles to match the object center coordinates to the center of the frame. 
pan_angle_desired = (object_x / frame_width) * 180 - 90  # assuming frame width is 200px
tilt_angle_desired = (object_y / frame_height) * 180 - 90 # assuming frame height is 200px

# Move the servos to match the desired angles
for servo in servos:
    servo.set_angle(pan_angle_desired, tilt_angle_desired)
    time.sleep(0.5) # wait for servo to settle

# Keep track of the current pan and tilt angles
pan_angle, tilt_angle = mav.get_servo_positions()

# Continuously update the servos to keep the object in the center of the frame
while True:
    # Get the current object center coordinates in the bounding box
    object_x = (x1 + x2) / 2
    object_y = (y1 + y2) / 2

    # Calculate the desired pan and tilt angles to match the object center coordinates to the center of the frame. 
    pan_angle_desired = (object_x / frame_width) * 180 - 90  # assuming frame width is 200px
    tilt_angle_desired = (object_y / frame_height) * 180 - 90 # assuming frame height is 200px

    # Check if the current servo positions match the desired position. If not, move the servos
    if abs(pan_angle - pan_angle_desired) > 1 or abs(tilt_angle - tilt_angle_desired) > 1:
        for servo in servos:
            servo.set_angle(pan_angle_desired, tilt_angle_desired)
            time.sleep(0.5) # wait for servo to settle

    # Update the current pan and tilt angles
    pan_angle, tilt_angle = mav.get_servo_positions()


""" import mavlink
from pymavlink import mavutil
import time

# Connect to the MAVLink connection
master = mavutil.mavlink_connection('udp:localhost:14550')

# Wait for heartbeats from the autopilot to synchronize state
master.wait_heartbeat()

# Get current servo positions
servo1_position = master.recv_match(type='SERVO_OUTPUT_RAW', blocking=True).servo1_raw
servo2_position = master.recv_match(type='SERVO_OUTPUT_RAW', blocking=True).servo2_raw

# Get object coordinates from detection of object bounded by boxes
x = 10 # x coordinate of the object 
y = 20 # y coordinate of the object 

# Update servo positions to match object's position to the center 
if x > 0 and y > 0: 
    servo1_position += 1 
    servo2_position += 1 
elif x < 0 and y < 0: 
    servo1_position -= 1 
    servo2_position -= 1 
else: 
    pass

# Set the servo positions with MAVLink messages 
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
    0, # Ignored 
    0, # Ignored
    servo1_position, # Servo1 position (in microseconds) 
    0, # Ignored 
    servo2_position, # Servo2 position (in microseconds) 
    0, # Ignored 
    0, # Ignored 
    0) # Ignored 

# Wait for the command to be received and processed 
time.sleep(1) """

""" import mavlink
import time

# Initialize the mavlink connection
mav = mavlink.MAVLink(0, 0)

# Setup servos for the object detection
servo_1 = 0
servo_2 = 1

# Set the servos' initial positions
mav.servo_output_raw(servo_1, 0)
mav.servo_output_raw(servo_2, 0)

# Wait for the object to be detected by the camera
while not object_detected:
    time.sleep(1)

# Get the location of the object in box coordinates 
x, y = object_location()

# Calculate the amount of movement needed to move the object to the center of the box 
dx = x - 0.5  # Desired x coordinate is 0.5 for centering
dy = y - 0.5  # Desired y coordinate is 0.5 for centering

# Calculate the servo positions based on the amount of movement needed 
servo_1_pos = dx * 100  # Servo 1 controls x-axis movement 
servo_2_pos = dy * 100  # Servo 2 controls y-axis movement 

# Send the servo position commands to the servos 
mav.servo_output_raw(servo_1, servo_1_pos)
mav.servo_output_raw(servo_2, servo_2_pos)

# Wait for the servos to finish their movement
while not servos_finished_moving():
    time.sleep(1)

print('Object has been moved to the center of the box.') """



""" #importing libraries
import mavlink
import time

#creating connection object with mavlink
my_conn = mavlink.MAVLink(0, 0)

#function to control servos
def controlServo(object_coordinates):

    #calculating the difference in the x and y co-ordinates of the object and the center of the camera frame
    x_diff = object_coordinates[0] - center_coordinates[0]
    y_diff = object_coordinates[1] - center_coordinates[1]

    #if the difference is more than a certain threshold, move plane to match the object to the center
    if (x_diff > threshold) or (y_diff > threshold):

        #sending mavlink message for controlling servos
        my_conn.mav.servo_output_raw_send(my_conn.target_system, my_conn.target_component, 0, int(x_diff * servo_gain), 1000, 2000, 3000, 4000)
        my_conn.mav.servo_output_raw_send(my_conn.target_system, my_conn.target_component, 1, int(y_diff * servo_gain), 1000, 2000, 3000, 4000)

        #waiting for some time
        time.sleep(0.5)

    else:
        print("Object is already at the center")

if __name__ == '__main__':

    #co-ordinates of the center of the frame
    center_coordinates = (320, 240)

    #threshold for the movement of the servos
    threshold = 10

    #gain for controlling the servos
    servo_gain = 10

    #infinite loop
    while True:

        #get the object coordinates from the object detector
        object_coordinates = getObjectCoordinates()

        #call the controlServo() function with the co-ordinates of the object
        controlServo(object_coordinates) """

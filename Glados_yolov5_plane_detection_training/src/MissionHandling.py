import time 
from dronekit import connect ,VehicleMode , LocationGlobalRelative ,Command ,LocationGlobal ,Channels
from pymavlink import mavutil

change_flag = False
alt_change_request = 0

#-- Key event function
def key(event):
    if event.char == event.keysym: #-- standard keys
        if event.keysym == 'r':
            print("r pressed >> Set the vehicle to RTL")
            vehicle.mode = VehicleMode("RTL")
            
    else: #-- non standard keys
        if event.keysym == 'Up':
            set_velocity_body(vehicle, gnd_speed, 0, 0)
        elif event.keysym == 'Down':
            set_velocity_body(vehicle,-gnd_speed, 0, 0)
        elif event.keysym == 'Left':
            set_velocity_body(vehicle, 0, -gnd_speed, 0)
        elif event.keysym == 'Right':
            set_velocity_body(vehicle, 0, gnd_speed, 0)

 #-- Define the function for sending mavlink velocity command in body frame
def set_velocity_body(vehicle, vx, vy, vz):
    """ Remember: vz is positive downward!!!
    http://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html
    
    Bitmask to indicate which dimensions should be ignored by the vehicle 
    (a value of 0b0000000000000000 or 0b0000001000000000 indicates that 
    none of the setpoint dimensions should be ignored). Mapping: 
    bit 1: x,  bit 2: y,  bit 3: z, 
    bit 4: vx, bit 5: vy, bit 6: vz, 
    bit 7: ax, bit 8: ay, bit 9:
    
    
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
            0,
            0, 0,
            mavutil.mavlink.MAV_FRAME_BODY_NED,
            0b0000111111000111, #-- BITMASK -> Consider only the velocities
            0, 0, 0,        #-- POSITION
            vx, vy, vz,     #-- VELOCITY
            0, 0, 0,        #-- ACCELERATIONS
            0, 0)
    vehicle.send_mavlink(msg)
    vehicle.flush()

def change_alt_in_continued_route(altitude):
    alt_change_cmd = Command(0,0,0,mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_CONTINUE_AND_CHANGE_ALT ,0,0,alt_change_request,0,0,0,0,0,altitude)
    cmds.add(alt_change_cmd)
    cmds.upload()

def arm_and_takeoff(altitude):
    while not vehicle.is_armable:
        print("waiting to be armable")
        time.sleep(1)
    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    while not vehicle.armed: time.sleep(1)
    cmds = vehicle.commands    
    cmds.clear()
    takeoff_cmd = Command(0,0,0,mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF ,0,0,10,0,0,0,vehicle.location.global_frame.lat+0.01,vehicle.location.global_frame.lon+0.01,altitude)
    cmds.add(takeoff_cmd)
    cmds.upload()
    time.sleep(2)
    print("Taking off")
    vehicle.mode = VehicleMode("TAKEOFF")
    #vehicle.mode = VehicleMode("AUTO")
    #vehicle.simple_takeoff(altitude)
    
    while True:
        v_alt = vehicle.location.global_relative_frame.alt
        print(">> Altitude = %.1f m"%v_alt)
        if v_alt >= altitude - 40.0:
            vehicle.mode = VehicleMode("AUTO")
        if v_alt >= altitude - 1.0:
            print("Target altitude reached")
            break
        time.sleep(1)

def clear_mission(vehicle):
    cmds = vehicle.commands
    vehicle.commands.clear()
    cmds.clear()
    vehicle.flush()
    download_mission(vehicle)

def download_mission(vehicle):
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()

def get_current_mission(vehicle):
    print("Downloading the mission")
    download_mission(vehicle)
    missionList = []
    n_wp = 0
    for wp in vehicle.commands:
        missionList.append(wp)
        n_wp +=1
    return n_wp,missionList

def add_last_waypoint_to_mission(                                       #--- Adds a last waypoint on the current mission file
        vehicle,            #--- vehicle object
        wp_Last_Latitude,   #--- [deg]  Target Latitude
        wp_Last_Longitude,  #--- [deg]  Target Longitude
        wp_Last_Altitude):  #--- [m]    Target Altitude
    """
    Upload the mission with the last WP as given and outputs the ID to be set
    """
    # Get the set of commands from the vehicle
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()

    # Save the vehicle commands to a list
    missionlist=[]
    for cmd in cmds:
        missionlist.append(cmd)

    # Modify the mission as needed. For example, here we change the
    wpLastObject = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 
                           wp_Last_Latitude, wp_Last_Longitude, wp_Last_Altitude)
    missionlist.append(wpLastObject)

    # Clear the current mission (command is sent when we call upload())
    cmds.clear()

    #Write the modified mission and flush to the vehicle
    for cmd in missionlist:
        cmds.add(cmd)
    cmds.upload()
    
    return (cmds.count)   

def check_incoming_command(vehicle):
    
    cmds = vehicle.commands

    
    download_mission(vehicle)
    

    def check_mission_commands(conn, name , m):
#        print("Got  message: %s" % (str(m),))
        if m.type != 0:
            print("Error uploading mission item: %d" % (m.type))

    def supply_mission_command(conn, name , m):
        global change_flag
        print("Got  request for mission item: %s" % (str(m),))
        change_flag = True

    vehicle.add_message_listener('MISSION_ACK', check_mission_commands)
    vehicle.add_message_listener('MISSION_REQUEST', supply_mission_command)

    return (cmds.count)

def ChangeMode(vehicle,mode):
    while vehicle.mode != VehicleMode(mode):
        vehicle.mode = VehicleMode(mode)
        time.sleep(0.5)
    
    return True
def load_parameters(vehicle):
    
    #vehicle.parameters["AUTO_OPTIONS"] = 3 #Allowtakeoffwithoutthrottle
    vehicle.parameters["MIS_OPTIONS"] = 4 #AllowMissionAfterLand
    vehicle.parameters["SIM_SPEEDUP"] = 2 #Simulation speed
    vehicle.parameters["RTL_AUTOLAND"] = 1 #plane will first RTL as normal, then when it starts circling the return point (home or a rally point) it will then switch to the AUTO mission after the DO_LAND_START and land
    vehicle.parameters["LAND_ABORT_THR"] = 1
    vehicle.groundspeed = 0
    vehicle.airspeed = 0
    
gnd_speed = 20
mode = 'GROUND'
vehicle = connect('udp:127.0.0.1:14550',wait_ready=True)
status = "OnGround"
camera_triggered = False
count = 0
servo_position = 0
gps_list = []
while True:
    #print("Vehicle Battery is %{}".format(vehicle.battery))
    gps_list.append((vehicle.location.global_frame.lat,vehicle.location.global_frame.lon))
    if camera_triggered == True :
        print("Camera triggered")
        servo_position = 1300
        #msg = vehicle.message_factory.command_long_encode(  0, 0,    # target_system, target_component
                                                            #mavutil.mavlink.MAV_CMD_DO_SET_SERVO, #command
                                                            #0, #confirmation
                                                            #1,    # servo number
                                                            #servo_position,          # servo position between 1000 and 2000
                                                            #0, 0, 0, 0, 0)    # param 3 ~ 7 not used
        # send command to vehicle
        #vehicle.send_mavlink(msg)
        mode = "UPDATE"
    """ elif camera_triggered == False :
        if status == "OnAir":
            mode = "UPDATE"
        if status == "OnGround":
            mode = "GROUND"  """
    if mode == 'GROUND':
        #clear_mission(vehicle)
        load_parameters(vehicle)
        n_wp , missionList = get_current_mission(vehicle)
        time.sleep(2)

        if n_wp > 0:
            print("A valid mission has been uploaded: takeoff")
            mode = "TAKEOFF"
    elif mode == 'TAKEOFF':
        #get_current_mission(vehicle)
         #-- Add a fake waypoint at the end of the mission
        add_last_waypoint_to_mission(vehicle, vehicle.location.global_relative_frame.lat, 
                                       vehicle.location.global_relative_frame.lon, 
                                       vehicle.location.global_relative_frame.alt)
        check_incoming_command(vehicle)
        time.sleep(1)
        
        arm_and_takeoff(60)
        status = "OnAir"
        #-- Change the UAV mode to AUTO
        print("Changing to AUTO")
        ChangeMode(vehicle,"AUTO")
        vehicle.groundspeed = gnd_speed
        mode = "MISSION"
        print("Switch to MISSION Mode")
    elif mode == 'UPDATE':
        print("Mission updated")
        vehicle.airspeed = 20
        n_wp , missionList = get_current_mission(vehicle)
        time.sleep(2)
        print(n_wp)
        if n_wp > 0:
            vehicle.commands.next = 0
            ChangeMode(vehicle,"AUTO")
            print("A valid mission has been uploaded: carry on")
            mode = "MISSION"
        if n_wp == 0:
            print("Waiting for a valid mission")
            mode = "MISSION"
    elif mode == 'MISSION':
        if change_flag == True:
            mode = 'UPDATE'
            change_flag = False
        
        print("Current WP : %d of % d "%(vehicle.commands.next,vehicle.commands.count))
        if ( vehicle.commands.next  == vehicle.commands.count) and change_flag == False:
            print("Final wp reached:deciding behaivour")
            clear_mission(vehicle)
            vehicle.commands.next = 0
            print("Mission ended")
            vehicle_location = vehicle.location.global_relative_frame
            #vehicle.parameters["RTL_AUTOLAND"] = 2
            cmds = vehicle.commands
            cmds.clear()
            print("Waiting for a mission")
            if vehicle.battery.level < 20:
                pass
            else :
                ChangeMode(vehicle,"RTL")
            change_flag = False
            mode = "WAITING"
        
    elif mode == "WAITING":
        count += 1
        if count == 20:
            camera_triggered = True
        if count == 40:
            camera_triggered = False
            count = 0
        print("Waiting")
        if change_flag == True:
                mode = 'UPDATE'
                change_flag = False
        if vehicle.battery.level < 20:
            
            print("Battery Level Low : go back home")
            land_flag = True
            
            wp = Command(0,0,0,mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND,0,0,0,0,0,0,vehicle.home_location.lat,vehicle.home_location.lon,vehicle.home_location.alt)
            #wp = Command(0,0,0,mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_VTOL_LAND,0,0,0,0,0,0,vehicle.home_location.lat,vehicle.home_location.lon,vehicle.home_location.alt)
            cmds.add(wp)
            cmds.upload()
            #ChangeMode(vehicle, "RTL")
            mode = 'BACK'
    elif mode == 'BACK':
        if vehicle.mode == "RTL" and land_flag == True:
            ChangeMode(vehicle,"AUTO")
            land_flag = False
        if vehicle.location.global_relative_frame.alt <1.0:
            mode= "GROUND"
            ChangeMode(vehicle,"MANUAL")
            vehicle.armed = False
            print(gps_list)
    time.sleep(0.5)
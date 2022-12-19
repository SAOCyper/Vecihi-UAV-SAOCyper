import time 
from dronekit import connect ,VehicleMode , LocationGlobalRelative ,Command ,LocationGlobal ,Channels
from pymavlink import mavutil

def arm_and_takeoff(altitude):
    while not vehicle.is_armable:
        print("waiting to be armable")
        time.sleep(1)
    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    while not vehicle.armed: time.sleep(1)

    print("Taking off")
    vehicle.simple_takeoff(altitude)
    while True:
        v_alt = vehicle.location.global_relative_frame.alt
        print(">> Altitude = %.1f m"%v_alt)
        if v_alt >= altitude - 1.0:
            print("Target altitude reached")
            break
        time.sleep(1)

def clear_mission(vehicle):
    cmds = vehicle.commands
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

def add_last_waypoint_to_mission(vehicle,lat,long,alt):
    download_mission()
    cmds = vehicle.commands

    #Save mission to a temporary list
    missionList = []
    for wp in cmds:
        missionList.append(wp)
    
    wp_last = Command(0,0,0,mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAY_POINT,0,0,0,0,0,0,lat,long,alt)
    missionList.append(wp_last)

    cmds.clear()
    for wp in missionList:
        cmds.add(wp)
    cmds.upload()

    return (cmds.count)

def ChangeMode(vehicle,mode):
    while vehicle.mode != VehicleMode(mode):
        vehicle.mode = VehicleMode(mode)
        time.sleep(0.5)
    
    return True

gnd_speed = 20
mode = 'GROUND'
vehicle = connect('udp:127.0.0.1:14551')

while True:
    if mode == 'GROUND':
        n_wp , missionList = get_current_mission(vehicle)
        time.sleep(2)

        if n_wp > 0:
            print("A valid mission has been uploaded: takeoff")
    elif mode == 'TAKEOFF':
        add_last_waypoint_to_mission(vehicle,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon,vehicle.location.global_relative_frame.alt)
        print("Final waypoint added to the curren mission")
        time.sleep(1)

        arm_and_takeoff(60)

        ChangeMode(vehicle,"AUTO")
        vehicle.groundspeed = gnd_speed
        mode = "MISSION"
        print("Swithc to MISSION Mode")

    elif mode == 'MISSION':
        print("Current WP : %d of % d "%(vehicle.commands.next,vehicle.commands.count))
        if ( vehicle.commands.next != vehicle.commands.count):
            print("Final wp reached:go back home")
            clear_mission(vehicle)
            print("Mission deleted")

            ChangeMode(vehicle, "RTL")
            mode = 'BACK'

    elif mode == 'BACK':
        if vehicle.location.global_relative_frame.alt <1.0:
            print("Vehicle landed")
            mode= "GROUND"
    time.sleep(1)
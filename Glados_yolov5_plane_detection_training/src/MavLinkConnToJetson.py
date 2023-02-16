from dronekit import connect, VehicleMode, LocationGlobalRelative, Command, Battery, LocationGlobal, Attitude
from pymavlink import mavutil
import time , socket , threading , pickle , math , psutil , argparse , copy
import numpy as np 


class Plane():

    def __init__(self, connection_string=None, vehicle=None):
        """ Initialize the object
        Use either the provided vehicle object or the connections tring to connect to the autopilot
        
        Input:
            connection_string       - the mavproxy style connection string, like tcp:127.0.0.1:5760
                                      default is None
            vehicle                 - dronekit vehicle object, coming from another instance (default is None)
        
        
        """
        
        #---- Connecting with the vehicle, using either the provided vehicle or the connection string
        if not vehicle is None:
            self.vehicle    = vehicle
            print("Using the provided vehicle")
        elif not connection_string is None:
            
            print("Connecting with vehicle...")
            self._connect(connection_string)
        else:
            raise("ERROR: a valid dronekit vehicle or a connection string must be supplied")
            return
            
        self._setup_listeners()

        self.airspeed           = 0.0       #- [m/s]    airspeed
        self.groundspeed        = 0.0       #- [m/s]    ground speed
        
        self.pos_lat            = 0.0       #- [deg]    latitude
        self.pos_lon            = 0.0       #- [deg]    longitude
        self.pos_alt_rel        = 0.0       #- [m]      altitude relative to takeoff
        self.pos_alt_abs        = 0.0       #- [m]      above mean sea level
        
        self.att_roll_deg       = 0.0       #- [deg]    roll
        self.att_pitch_deg      = 0.0       #- [deg]    pitch
        self.att_heading_deg    = 0.0       #- [deg]    magnetic heading
        
        self.wind_dir_to_deg    = 0.0       #- [deg]    wind direction (where it is going)
        self.wind_dir_from_deg  = 0.0       #- [deg]    wind coming from direction
        self.wind_speed         = 0.0       #- [m/s]    wind speed
        
        self.climb_rate         = 0.0       #- [m/s]    climb rate
        self.throttle           = 0.0       #- [ ]      throttle (0-100)
        
        self.ap_mode            = ''        #- []       Autopilot flight mode
        
        self.mission            = self.vehicle.commands #-- mission items
        
        self.location_home      = LocationGlobalRelative(0,0,0) #- LocationRelative type home
        self.location_current   = LocationGlobalRelative(0,0,0) #- LocationRelative type current position
        
    def _connect(self, connection_string):      #-- (private) Connect to Vehicle
        """ (private) connect with the autopilot
        
        Input:
            connection_string   - connection string (mavproxy style)
        """
        self.vehicle = connect(connection_string, wait_ready=True, heartbeat_timeout=60)
        self._setup_listeners()
        
    def _setup_listeners(self):                 #-- (private) Set up listeners
        #----------------------------
        #--- CALLBACKS
        #----------------------------
        if True:    
            #---- DEFINE CALLBACKS HERE!!!
            @self.vehicle.on_message('ATTITUDE')   
            def listener(vehicle, name, message):          #--- Attitude
                self.att_roll_deg   = math.degrees(message.roll)
                self.att_pitch_deg  = math.degrees(message.pitch)
                self.att_heading_deg = math.degrees(message.yaw)%360
                
            @self.vehicle.on_message('GLOBAL_POSITION_INT')       
            def listener(vehicle, name, message):          #--- Position / Velocity                                                                                                             
                self.pos_lat        = message.lat*1e-7
                self.pos_lon        = message.lon*1e-7
                self.pos_alt_rel    = message.relative_alt*1e-3
                self.pos_alt_abs    = message.alt*1e-3
                self.location_current = LocationGlobalRelative(self.pos_lat, self.pos_lon, self.pos_alt_rel)
                
                
            @self.vehicle.on_message('VFR_HUD')
            def listener(vehicle, name, message):          #--- HUD
                self.airspeed       = message.airspeed
                self.groundspeed    = message.groundspeed
                self.throttle       = message.throttle
                self.climb_rate     = message.climb 
                
            @self.vehicle.on_message('WIND')
            def listener(vehicle, name, message):          #--- WIND
                self.wind_speed         = message.speed
                self.wind_dir_from_deg  = message.direction % 360
                self.wind_dir_to_deg    = (self.wind_dir_from_deg + 180) % 360
                        
            
        return (self.vehicle)
        print(">> Connection Established")

    def _get_location_metres(self, original_location, dNorth, dEast, is_global=False):
        """
        Returns a Location object containing the latitude/longitude `dNorth` and `dEast` metres from the
        specified `original_location`. The returned Location has the same `alt and `is_relative` values
        as `original_location`.
        The function is useful when you want to move the vehicle around specifying locations relative to
        the current vehicle position.
        The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
        For more information see:
        http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
        """
        earth_radius=6378137.0 #Radius of "spherical" earth
        #Coordinate offsets in radians
        dLat = dNorth/earth_radius
        dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

        #New position in decimal degrees
        newlat = original_location.lat + (dLat * 180/math.pi)
        newlon = original_location.lon + (dLon * 180/math.pi)
        
        if is_global:
            return LocationGlobal(newlat, newlon,original_location.alt)    
        else:
            return LocationGlobalRelative(newlat, newlon,original_location.alt)         
        
    def is_armed(self):                         #-- Check whether uav is armed
        """ Checks whether the UAV is armed
        
        """
        return(self.vehicle.armed)
        
    def arm(self):                              #-- arm the UAV
        """ Arm the UAV
        """
        self.vehicle.armed = True
        
    def disarm(self):                           #-- disarm UAV
        """ Disarm the UAV
        """
        self.vehicle.armed = False

    def set_airspeed(self, speed):              #--- Set target airspeed
        """ Set uav airspeed m/s
        """
        self.vehicle.airspeed = speed
        
    def set_ap_mode(self, mode):                #--- Set Autopilot mode
        """ Set Autopilot mode
        """
        time_0 = time.time()
        try:
            tgt_mode    = VehicleMode(mode)
        except:
            return(False)
            
        while (self.get_ap_mode() != tgt_mode):
            self.vehicle.mode  = tgt_mode
            time.sleep(0.2)
            if time.time() < time_0 + 5:
                return (False)

        return (True)
        
    def get_ap_mode(self):                      #--- Get the autopilot mode
        """ Get the autopilot mode
        """
        self._ap_mode  = self.vehicle.mode
        return(self.vehicle.mode)
        
    def clear_mission(self):                    #--- Clear the onboard mission
        """ Clear the current mission.
        
        """
        cmds = self.vehicle.commands
        self.vehicle.commands.clear()
        self.vehicle.flush()

        # After clearing the mission you MUST re-download the mission from the vehicle
        # before vehicle.commands can be used again
        # (see https://github.com/dronekit/dronekit-python/issues/230)
        self.mission = self.vehicle.commands
        self.mission.download()
        self.mission.wait_ready()

    def download_mission(self):                 #--- download the mission
        """ Download the current mission from the vehicle.
        
        """
        self.vehicle.commands.download()
        self.vehicle.commands.wait_ready() # wait until download is complete.  
        self.mission = self.vehicle.commands

    def mission_add_takeoff(self, takeoff_altitude=50, takeoff_pitch=15, heading=None):
        """ Adds a takeoff item to the UAV mission, if it's not defined yet
        
        Input:
            takeoff_altitude    - [m]   altitude at which the takeoff is considered over
            takeoff_pitch       - [deg] pitch angle during takeoff
            heading             - [deg] heading angle during takeoff (default is the current)
        """
        if heading is None: heading = self.att_heading_deg
        
        self.download_mission()
        #-- save the mission: copy in the memory
        tmp_mission = list(self.mission)
        
        print(tmp_mission.count)
        is_mission  = False
        if len(tmp_mission) >= 1:
            is_mission = True
            print("Current mission:")
            for item in tmp_mission:
                print( item)
            #-- If takeoff already in the mission, do not do anything
            
        if is_mission and tmp_mission[0].command == mavutil.mavlink.MAV_CMD_NAV_TAKEOFF:
            print ("Takeoff already in the mission")
        else:
            print("Takeoff not in the mission: adding")
            self.clear_mission()
            takeoff_item = Command( 0, 0, 0, 3, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, takeoff_pitch,  0, 0, heading, 0,  0, takeoff_altitude)
            self.mission.add(takeoff_item)
            for item in tmp_mission:
                self.mission.add(item)
            self.vehicle.flush()
            print(">>>>>Done")
        
    def arm_and_takeoff(self, altitude=50, pitch_deg=12):
        """ Arms the UAV and takeoff
        Planes need a takeoff item in the mission and to be set into AUTO mode. The 
        heading is kept constant
        
        Input:
            altitude    - altitude at which the takeoff is concluded
            pitch_deg   - pitch angle during takeoff
        """
        self.mission_add_takeoff(takeoff_altitude=1.5*altitude, takeoff_pitch=pitch_deg)
        print ("Takeoff mission ready")
        
        while not self.vehicle.is_armable:
            print("Wait to be armable...")
            time.sleep(1.0)
            
        
        #-- Save home
        while self.pos_lat == 0.0:
            time.sleep(0.5)
            print ("Waiting for good GPS...")
        self.location_home      = LocationGlobalRelative(self.pos_lat,self.pos_lon,altitude)
        
        print("Home is saved as "), self.location_home
        print ("Vehicle is Armable: try to arm")
        self.set_ap_mode("MANUAL")
        n_tries = 0
        while not self.vehicle.armed:
            print("Try to arm...")
            self.arm()
            n_tries += 1
            time.sleep(2.0) 
            
            if n_tries > 5:
                print("!!! CANNOT ARM")
                break
                
        #--- Set to auto and check the ALTITUDE
        if self.vehicle.armed: 
            print ("ARMED")
            self.set_ap_mode("AUTO")
            
            while self.pos_alt_rel <= altitude - 20.0:
                print ("Altitude = %.0f"%self.pos_alt_rel)
                time.sleep(2.0)
                
            print("Altitude reached: set to GUIDED")
            self.set_ap_mode("GUIDED")
            
            time.sleep(1.0)
            
            print("Sending to the home")
            self.vehicle.simple_goto(self.location_home)
            
        return True
        
    def get_target_from_bearing(self, original_location, ang, dist, altitude=None):
        """ Create a TGT request packet located at a bearing and distance from the original point
        
        Inputs:
            ang     - [rad] Angle respect to North (clockwise) 
            dist    - [m]   Distance from the actual location
            altitude- [m]
        Returns:
            location - Dronekit compatible
        """
        
        if altitude is None: altitude = original_location.alt
        
        # print '---------------------- simulate_target_packet'
        dNorth  = dist*math.cos(ang)
        dEast   = dist*math.sin(ang)
        # print "Based on the actual heading of %.0f, the relative target's coordinates are %.1f m North, %.1f m East" % (math.degrees(ang), dNorth, dEast) 
        
        #-- Get the Lat and Lon
        tgt     = self._get_location_metres(original_location, dNorth, dEast)
        
        tgt.alt = altitude
        # print "Obtained the following target", tgt.lat, tgt.lon, tgt.alt

        return tgt      

    def ground_course_2_location(self, angle_deg, altitude=None):
        """ Creates a target to aim to in order to follow the ground course
        Input:
            angle_deg   - target ground course
            altitude    - target altitude (default the current)
        
        """
        tgt = self.get_target_from_bearing(original_location=self.location_current, 
                                             ang=math.radians(angle_deg), 
                                             dist=5000,
                                             altitude=altitude)
        return(tgt)
        
    def goto(self, location):
        """ Go to a location
        
        Input:
            location    - LocationGlobal or LocationGlobalRelative object
        
        """
        self.vehicle.simple_goto(location)
 
    def set_ground_course(self, angle_deg, altitude=None):
        """ Set a ground course
        
        Input:
            angle_deg   - [deg] target heading
            altitude    - [m]   target altitude (default the current)
        
        """
        
        #-- command the angles directly
        self.goto(self.ground_course_2_location(angle_deg, altitude))
        
    def get_rc_channel(self, rc_chan, dz=0, trim=1500):         #--- Read the RC values from the channel
        """
        Gets the RC channel values with a dead zone around trim
        
        Input:
            rc_channel  - input rc channel number
            dz          - dead zone, within which the output is set equal to trim
            trim        - value about which the dead zone is evaluated
            
        Returns:
            rc_value    - [us]
        """
        if (rc_chan > 16 or rc_chan < 1):
            return -1
        
        #- Find the index of the channel
        strInChan = '%1d' % rc_chan
        try:
        
            rcValue = int(self.vehicle.channels.get(strInChan))
            
            if dz > 0:
                if (math.fabs(rcValue - trim) < dz):
                    return trim
            
            return rcValue
        except:
            return 0     
    
    def set_rc_channel(self, rc_chan, value_us=0):      #--- Overrides a rc channel (call with no value to reset)
        """
        Overrides the RC input setting the provided value. Call with no value to reset
        
        Input:
            rc_chan     - rc channel number
            value_us    - pwm value 
        """
        strInChan = '%1d' % rc_chan
        self.vehicle.channels.overrides[strInChan] = int(value_us)
                
    def clear_all_rc_override(self):               #--- clears all the rc channel override
        self.vehicle.channels.overrides = {}

def uav_server():
        global data
        host_uav ="127.0.0.1"
        port_uav = 65433
        lsock_uav = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock_uav.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock_uav.bind((host_uav, port_uav))
        lsock_uav.listen(2)
        print(f"Listening on UAV {(host_uav, port_uav)}")
        conn, address = lsock_uav.accept()  # accept new connection
        print("Connection from: " + str(address))
        data_prev = 0
        while True:
            # receive data stream. it won't accept data packet greater than 4096 bytes
            data = conn.recv(8192)
            data = pickle.loads(data) 
            #print(data)
            if data_prev != data:
                """ if type(data) == list:
                    behaivour_dict=drive.flight_controller(incoming_data=data)
                    data_prev = data """
            time.sleep(0.807)
            if not data:
                # if data is not received break
                break 
            print("Incoming Ground Control Station Data")
            

        conn.close()  # close the connection
target_lat = 0
target_lon = 0
target_alt = 50 
mode = "IDLE"


#####Servo Bağlantıları Değerler#######
Aileron_port = 1
Elevator_port = 2
Throttle_port = 3
Rudder_port =  4
#######GELEN VERİLER########
incoming_roll = 1500
incoming_yaw = 1500
incoming_pitch = 1500
incoming_altitude = 100
incoming_latitude = 39.85324
incoming_long = 32.78342
incoming_request = "Object"
incoming_attitude_list = ["Turn Right","Turn Left","Turn Right Above","Turn Left Above","Turn Right Below","Turn Left Below","Descend","Ascend","Straight","Tilt Right","Tilt Left"]
incoming_wait_ready_request = "Object"

#####Default Values#########
max_roll_val = 1800
default_roll_val =  1560
min_roll_val = 1320
max_pitch_value = 1600
default_pitch_val = 1500
min_pitch_val = 1200
max_altitude = 200
max_yaw_value = 1800
default_yaw_value = 1500
min_yaw_value = 1200
cruise_altitude = 100
cruise_angle_deg= 0.0
delta_angle_deg = 40.0
land_count = 0
cmd_set = False
landed = False
if __name__ == '__main__':
    thread_server = threading.Thread(target=uav_server)
    thread_server.start()
    parser = argparse.ArgumentParser()
    parser.add_argument('--connect', default='tcp:127.0.0.1:5762')
    args = parser.parse_args()
    connection_string = args.connect
    #-- Create the object
    plane = Plane(connection_string)
    #-- Arm and takeoff
    if not plane.is_armed(): plane.arm_and_takeoff()
    time.sleep(5)
    #-- Set in Guided and test the ground course
    plane.set_ap_mode("GUIDED")
    a = 0 ###TEMP DELETE LATER
    incoming_direction = "Turn Right"
    plane.set_rc_channel(4,default_pitch_val)
    while True:
        if incoming_request == "Object":
            
            if  plane.vehicle.battery.level < 20 and landed == False:
                plane.set_ap_mode("AUTO")
                if plane.get_ap_mode() == "AUTO" and land_count <1:
                    print("RTL mode sended")
                    if plane.pos_alt_rel > 100:
                        plane.set_rc_channel(2 , 1200)
                        time.sleep(1.5)
                        print(plane.vehicle._pitch)
                        plane.set_rc_channel(2,)
                        print(plane.vehicle._pitch)
                    land_count = land_count + 1
                    plane.set_ap_mode("RTL")
                    cmd_set = True
                    mode = "LAND"
            relative_pitch = default_pitch_val    
            if mode == "IDLE":
                print("Plane is IDLE")
                print ("Heading to %.0fdeg"%cruise_angle_deg)
                plane.set_ground_course(cruise_angle_deg, cruise_altitude)
                time.sleep(5)
                cruise_angle_deg    += delta_angle_deg
                a = a+1
                if a == 2:
                    mode = "TRACKING"
            elif mode == "TRACKING":
                plane.set_ap_mode("FBWB")
                i=0 
                roll_val  = default_roll_val
                
                if incoming_direction == incoming_attitude_list[0] :
                    roll_val = 1300
                    plane.set_rc_channel(4,roll_val)
                    i = i + 1
                elif incoming_direction == incoming_attitude_list[1] :
                    roll_val = 1700
                    plane.set_rc_channel(4,roll_val)
                    
                if i > 30:
                    incoming_direction = "Turn Left"
                    i = 0
                """ while i < 30:
                    roll_val = incoming_roll
                    if roll_val > max_roll_val:
                        roll_val = max_roll_val   
                    print("mode 1")
                    plane.set_rc_channel(4,roll_val)
                    #LastThrottle=plane.vehicle.channels.overrides[1]
                    time.sleep(1)
                    i = i +1 """
                """ i = 0 
                roll_val  = default_roll_val
                while i < 30:
                    roll_val = roll_val - 30 
                    if roll_val < min_roll_val:
                        roll_val = min_roll_val   
                    print("mode 1")
                    #plane.set_rc_channel(2, default_pitch)
                    #plane.set_rc_channel(3 , 1700)
                    #plane.set_rc_channel(1 , roll_val)
                    #plane.set_rc_channel(2,roll_val)
                    plane.set_rc_channel(4,roll_val)
                    #LastThrottle=plane.vehicle.channels.overrides[1]
                    #print(LastThrottle)
                    time.sleep(1)
                    i = i +1
                roll_val = 1530 """
                """ i = 0                
                while i < 15:
                    print("mode 3")
                    #plane.set_rc_channel(1, 1700)
                    
                    #plane.set_rc_channel(3, 1800)
                    
                    if plane.pos_alt_rel > 100 :
                        relative_pitch = relative_pitch + 1
                        plane.set_rc_channel(2, relative_pitch)
                    else:
                        relative_pitch = relative_pitch - 1
                        plane.set_rc_channel(2, relative_pitch)
                    i = i +1
                    time.sleep(1) """
            elif mode == "LAND":
                if cmd_set == True and plane.vehicle.location.global_relative_frame.alt < 50:
                    plane.set_ap_mode("AUTO")
                    plane.clear_mission()
                    
                    #cmds = plane.vehicle.commands
                    land_mission = Command(0,0,0,3, mavutil.mavlink.MAV_CMD_NAV_LAND,0,0,0,0,0,0,plane.location_home.lat,plane.location_home.lon,plane.location_home.alt)
                    plane.mission.add(land_mission)
                    #cmds.add(wp)
                    #cmds.upload()
                    plane.vehicle.flush()
                    print("Plane is descending")
                    cmd_set = False
                if plane.location_current.alt < 1:
                    landed = True
                    plane.set_ap_mode("Manual")
                    plane.disarm()
                    
        elif incoming_request == "GPS":
            pass        
    """ while True:
        target_location=LocationGlobalRelative(lat=target_lat,lon=target_lon,alt=target_alt)
        plane.goto() """

        
import tkinter,socket, pickle,tkintermapview,os,socket,sys,selectors,traceback,threading,sys,time,math,geopy.distance,cv2
sys.path.insert(1, r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\src\modules')
import telemetry_data
from math import sin, cos, sqrt, atan2, radians ,acos ,degrees,atan,asin
from datetime import datetime
import numpy as np
from numpy import mean
from geographiclib.geodesic import Geodesic
import matplotlib.pyplot as plt
from scipy.interpolate import *
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command, Battery, LocationGlobal, Attitude
from pymavlink import mavutil
import time , socket , threading , pickle , math , psutil , argparse , copy
import numpy as np 
import warnings
import quaternion
#Camera Global Paremeters
pitch_cam_angle = 0
roll_cam_angle = 0
camera_on_flag = False
camera_on_flag_time2 = 0
lock_on = False
lock_on_started = False
lock_on_finished = False
target_window_location = None
frame = 0
cap = 0
temp_m1 = 0.1
temp_m2 = 0.1
start = 0
info = datetime.now()
diff_info = 0
kilitlenme_sayısı = 0
kilitlenme = False
hedef_merkez_x = 0
hedef_merkez_y = 0
başlangıç_zamanı = 0
bitiş_zamanı = 0
starting_point_flag = False
warnings.simplefilter('ignore', np.RankWarning)
####Command Variables########
incoming_roll = 1500
incoming_yaw = 1500
incoming_pitch = 1500
incoming_altitude = 0
incoming_latitude = 0
incoming_long = 32.78342
incoming_longitude = 0
incoming_enemy_id = 0
incoming_distance = 0
incoming_request = 0
incoming_attitude = 0
incoming_attitude_list = ["Turn Right","Turn Left","Turn Right Above","Turn Left Above","Turn Right Below","Turn Left Below","Descend","Ascend","Straight","Tilt Right","Tilt Left"]
incoming_wait_ready_request = 0
target_lat = 0
target_lon = 0
target_alt = 50 
mode = "IDLE"
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
####Servo Ports##########
Aileron_port = 1
Elevator_port = 2
Throttle_port = 3
Rudder_port =  4


#Localizasyon Parameters
data = {"incoming_request":0,"incoming_altitude":0,"incoming_distance":0,"incoming_enemy_id":0,"incoming_longitude":0,"incoming_latitude":0}
enemy_list  = []
team_number = 1
prev_distance_list = {}
counter = 0
prev_coordinates = []
enemy_prev_list = []
previous_location_list = []
coordinates_prev = (0,0)
z = 0
k = 0
p = 0
count = 0


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
        self._load_parameters()
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
    def _load_parameters(self):
        self.vehicle.parameters["RNGFND_LANDING"] = 1
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
        self.vehicle.disarm(True)
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
        global starting_point_flag
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
        while starting_point_flag == False:
            self.home_landing_heading_angle = 0
            if self.att_heading_deg != 0:
                self.home_landing_heading_angle = self.att_heading_deg
                print("Aperture angle is {}".format(self.home_landing_heading_angle))
            if self.home_landing_heading_angle != 0:
                starting_point_flag = True 
        self.landing_starting_point = self.create_landing_starting_point()
        self.landing_starting_point = LocationGlobalRelative(self.landing_starting_point.lat,self.landing_starting_point.lon,self.landing_starting_point.alt)
        print(self.landing_starting_point)
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
    def distance_to_current_waypoint(self):
        """
        Gets distance in metres to the current waypoint. 
        It returns None for the first waypoint (Home location).
        """
        nextwaypoint = self.vehicle.commands.next
        if nextwaypoint==0:
            return None
        missionitem=self.vehicle.commands[nextwaypoint-1] #commands are zero indexed
        lat = missionitem.x
        lon = missionitem.y
        alt = missionitem.z
        targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
        distancetopoint = self.get_distance_metres2(self.vehicle.location.global_frame, targetWaypointLocation)
        return distancetopoint   
    def get_distance_metres2(self,aLocation1, aLocation2):
        """
        Returns the ground distance in metres between two LocationGlobal objects.
        This method is an approximation, and will not be accurate over large distances and close to the 
        earth's poles. It comes from the ArduPilot test code: 
        https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
        """
        dlat = aLocation2.lat - aLocation1.lat
        dlong = aLocation2.lon - aLocation1.lon
        return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5
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
    def create_landing_starting_point(self):
        
        land_start_point = self.get_target_from_bearing(original_location=self.location_home, 
                                             ang=math.radians(self.home_landing_heading_angle), 
                                             dist=600,
                                             altitude=60)
        return (land_start_point)   
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

    def get_distance_metres(self):
        """
        Returns the ground distance in metres between two LocationGlobal objects.
        This method is an approximation, and will not be accurate over large distances and close to the 
        earth's poles. It comes from the ArduPilot test code: 
        https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
        """
        dlat = self.location_current.lat - self.landing_starting_point.lat
        dlong = self.location_current.lon - self.landing_starting_point.lon
        return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

    def send_to_landing_point(self):
        horizontal_difference = self.get_distance_metres()
        #self.goto(self.landing_starting_point)
        second = int(horizontal_difference / plane.vehicle.airspeed)
        plane.set_airspeed(15)
        plane.set_ap_mode("AUTO")
        cmd=Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, self.landing_starting_point.lat, self.landing_starting_point.lon, 60)
        plane.mission.add(cmd)
        plane.vehicle.flush()
        time.sleep(1)
        if plane.get_ap_mode() == "RTL":
            plane.set_ap_mode("AUTO")
        distance_to_wp = self.distance_to_current_waypoint()
        while distance_to_wp == None :
            distance_to_wp = self.distance_to_current_waypoint()
        while distance_to_wp > 10 :
            if plane.get_ap_mode() == "RTL":
                plane.set_ap_mode("AUTO")
            distance_to_wp = self.distance_to_current_waypoint()
            if horizontal_difference < 10:
                break
            print(distance_to_wp)
            print("Arriving at landing point")
            time.sleep(0.1)
        print("Arrived at landing point.Attempting to land ...")
    def send_set_attitude_target(self,roll=0, pitch=0, yaw=0, thrust=0.5):
        attitude = [np.radians(roll), np.radians(pitch), np.radians(yaw)]
        a = quaternion.from_euler_angles(attitude)
        attitude_quaternion = quaternion.as_float_array(a)
        print(attitude_quaternion)
        msg = plane.vehicle.message_factory.set_attitude_target_encode(
            0, 0, 0,  # time_boot_ms, target_system, target_component
            0b10111000,  # type_mask https://mavlink.io/en/messages/common.html#ATTITUDE_TARGET_TYPEMASK
            attitude_quaternion,  # Attitude quaternion
            0, 0, 0,  # Rotation rates (ignored)
            thrust  # Between 0.0 and 1.0
        )

        self.vehicle.send_mavlink(msg)


class Camera():
    Angle = 0
    Direction = 0
    Time = 0
    Success = 0
    @staticmethod
    def _GPS_Saati():
        time_format = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        splitted = time_format.split(":")
        splitted1 = splitted[2].split('.')
        gps_saat = {"saat":splitted[0],"dakika":splitted[1],"saniye":splitted1[0],"milisaniye":splitted1[1]}
        return gps_saat
    def __init__(self):   
        global telemetry_packager 
        """ cv2.startWindowThread()
        cv2.namedWindow("preview") """

        self.trained_face_data = cv2.CascadeClassifier(r'C:\CYCLOP\GLADOS\haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)
        #self.telemetry_packager = TelemetryCreate()
        #self.recorder = cv2.VideoWriter('output.mp4',cv2.VideoWriter_fourcc('m','p','4','v'), 30.0,(640,480))
        self.KNOWN_DISTANCE = 52  # centimeter 
        self.KNOWN_WIDTH = 14.3  # centimeter     
        ref_image_face_width = 182 #pixel
        self.fpsArray = []
        self.averageFPS = 0
        self.focal_length_measured =self.focal_length(self.KNOWN_DISTANCE, self.KNOWN_WIDTH, ref_image_face_width)                              
        
    def focal_length(self,measured_distance, real_width, width_in_rf_image):
        """
        This Function Calculate the Focal Length(distance between lens to CMOS sensor), it is simple constant we can find by using
        MEASURED_DISTACE, REAL_WIDTH(Actual width of object) and WIDTH_OF_OBJECT_IN_IMAGE
        :param1 Measure_Distance(int): It is distance measured from object to the Camera while Capturing Reference image
        :param2 Real_Width(int): It is Actual width of object, in real world (like My face width is = 14.3 centimeters)
        :param3 Width_In_Image(int): It is object width in the frame /image in our case in the reference image(found by Face detector)
        :retrun focal_length(Float):"""
        focal_length_value = (width_in_rf_image * measured_distance) / real_width
        return focal_length_value
    
    def distance_finder(self,focal_length,real_face_width,face_width_in_pixel):
        """
        This Function simply Estimates the distance between object and camera using arguments(focal_length, Actual_object_width, Object_width_in_the_image)
        :param1 focal_length(float): return by the focal_length_Finder function
        :param2 Real_Width(int): It is Actual width of object, in real world (like My face width is = 5.7 Inches)
        :param3 object_Width_Frame(int): width of object in the image(frame in our case, using Video feed)
        :return Distance(float) : distance Estimated
        """
        distance = (real_face_width * focal_length) / face_width_in_pixel
        return distance
    def get_angle(self,pointlist:list):
        pt1, pt2, pt3 = pointlist[-3:]
        global frame,temp_m1,temp_m2
        if (pt2[0]-pt1[0])!= 0 and (pt3[0]-pt1[0]) != 0:
            m1 = (pt2[1]-pt1[1])/(pt2[0]-pt1[0])
            m2 = (pt3[1]-pt1[1])/(pt3[0]-pt1[0])
            temp_m1 = m1
            temp_m2 = m2
        angR = math.atan((temp_m2-temp_m1)/(1+(temp_m2*temp_m1)))
        angD = round(math.degrees(angR))
        direction = None
        if pt2[1] < pt1[1] and pt2[0] > pt1[0]:
            direction = "Q1"
        elif pt2[1] < pt1[1] and pt2[0] < pt1[0]:
            direction = "Q2"
        elif pt2[1] > pt1[1] and pt2[0] < pt1[0]:
            direction = "Q3"
        elif pt2[1] > pt1[1] and pt2[0] > pt1[0]:
            direction = "Q4"
        angD = abs(angD)
        #cv2.putText(frame,str(angD),(pt1[0]-40,pt1[1]-20),cv2.FONT_HERSHEY_COMPLEX,
                    #1.5,(0,0,255),2)
        return angD , direction
    
    def detect(self):
        global lock_on , lock_on_started , lock_on_finished , camera_on_flag , camera_on_flag_time2 , target_window_location
        global pitch_cam_angle , roll_cam_angle
        lock_on_time = 0
        lock_on_waiting_time = 0
        points_x = []
        point_count = 0
        frame_count = 0
        points_y = []
        current_bbox_frame = []
        prev_bbox_frame = []
        tracking_objects = {}
        track_id = 0
        x_list = [item for item in range(0,1300)]
        camera_on_flag_time = 0
        while True:
                # Capture frame-by-frame
                t0 = time.time()
                if len(current_bbox_frame) > 1000:
                    current_bbox_frame.clear()
                global frame , start , kilitlenme_sayısı ,kilitlenme ,diff_info ,hedef_merkez_x,hedef_merkez_y,başlangıç_zamanı,bitiş_zamanı
                ret, frame = self.cap.read()
                rows,cols,_ = (480,640,3)
                xmedium = int(cols/2)
                y_medium = int(rows/2)
                hitbox_right = int(cols - (cols/4))
                hitbox_left = int(cols/4)
                hitbox_up = int(rows/10)
                hitbox_down = int(rows - (rows/10))
                hitbox_sideway_1_bound_y = int(y_medium - 160)
                hitbox_sideway_2_bound_y = int(y_medium  + 160)
                hitbox_upper_bound_x_1 = int(xmedium - 160)
                hitbox_upper_bound_x_2 = int(xmedium + 160)
                hitbox_midpointx = int((hitbox_right + hitbox_left)/2)
                hitbox_midpointy = int((hitbox_up + hitbox_down) / 2)
                horizontalboundary1 =int((xmedium/25)*20)
                horizontalboundaryvar = int(xmedium - horizontalboundary1)
                horizontalboundary2 = int(xmedium + horizontalboundaryvar)
                verticalboundary1=int((y_medium/2))
                verticalboundary3=int((y_medium/4))
                verticalboundary4=int((y_medium*2))-verticalboundary3
                verticalboundary2=y_medium+verticalboundary1
                gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)            
                faces = self.trained_face_data.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=4)
                cv2.rectangle(frame,(hitbox_left,hitbox_up),(hitbox_right,hitbox_down),color=(255, 17, 255),thickness=3)
                cv2.putText(frame,text="Hit Zone",org=(hitbox_left,hitbox_down+35),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1,color=(255, 17, 255))
                if len(faces)>0:
                    camera_on_flag = True
                    frame_count += 1
                    for (x, y, w, h) in faces:
                        #print(x,y,w,h)
                        
                        success = False
                        roi_gray = gray[y:y+h, x:x+w] #(ycord_start, ycord_end)
                        roi_color = frame[y:y+h, x:x+w]
                        end_cord_x = x + w
                        end_cord_y = y + h
                        self.distance = self.distance_finder(self.focal_length_measured,self.KNOWN_WIDTH,w)
                        dikey = ((end_cord_y - y)/rows)*100
                        yatay = ((end_cord_x - x)/cols)*100
                        cv2.rectangle(frame, (x, y), (end_cord_x, end_cord_y), color=(0, 0, 255), thickness=2)###Hedef Karesi
                        cv2.putText(frame,text="Dikey = %{:.2f}".format(dikey),org=(end_cord_x+10, y+15),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(22,159,230),thickness=2,lineType=cv2.LINE_AA)
                        cv2.putText(frame,text="Yatay = %{:.2f}".format(yatay),org=(end_cord_x-70, y-15),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(22,159,2230),thickness=2,lineType=cv2.LINE_AA)
                        #print("Distance is {} cm".format(self.distance))
                        framemid_x = int((end_cord_x + x)/2)
                        framemid_y = int((end_cord_y + y)/2)
                        direction = "Middle"
                        movement_direction_x = 0
                        pixel_angle_rate_x = 40 / (cols/2)
                        pixel_angle_rate_y = 12 / (rows/2)
                        if framemid_x > (hitbox_midpointx + 20) :
                            x_pixel = int(cols - framemid_x)
                            roll_cam_angle = x_pixel * pixel_angle_rate_x
                        elif framemid_x < (hitbox_midpointx - 20):
                            x_pixel = int(framemid_x)
                            roll_cam_angle = (x_pixel * pixel_angle_rate_x) *  -1
                        elif framemid_x > (hitbox_midpointx - 20) and framemid_x < (hitbox_midpointx + 20):
                            roll_cam_angle = 0
                        if framemid_y < (hitbox_midpointy -20):
                            y_pixel = int(framemid_y)
                            pitch_cam_angle = y_pixel * pixel_angle_rate_y
                        elif framemid_y > (hitbox_midpointy + 20):
                            y_pixel = int(rows - framemid_y)
                            pitch_cam_angle = (y_pixel * pixel_angle_rate_y) * -1
                        elif framemid_y > (hitbox_midpointy -20) and framemid_y < (hitbox_midpointy + 20):
                            pitch_cam_angle = 0
                        """ if len(current_bbox_frame) > 1:
                            movement_direction_x = current_bbox_frame[-1][0] - prev_bbox_frame[-1][0]
                        if movement_direction_x > 0:
                            direction="Right"
                        else:
                            direction="Left" """
                        """ current_bbox_frame.append((framemid_x,framemid_y)) """
                        """ if frame_count <= 2:
                            for pt in current_bbox_frame:
                                for pt2 in prev_bbox_frame:
                                    distance = math.hypot(pt2[0]-pt[0],pt2[1]-pt[1])
                                    if distance < 20:
                                        tracking_objects[track_id] = pt
                                        track_id += 1
                        else:
                            tracking_objects_copy = tracking_objects.copy()
                            for object_id,pt2 in tracking_objects_copy.items():
                                object_exists = False
                                for pt in current_bbox_frame:
                                    distance = math.hypot(pt2[0]-pt[0],pt2[1]-pt[1])
                                    if distance < 20:
                                        tracking_objects[object_id] = pt
                                        object_exists = True
                                if not object_exists:
                                    tracking_objects.pop(object_id) """
                        """ for object_id , pt in tracking_objects.items():
                            cv2.putText(frame , str(object_id),(pt[0],pt[1]-7),0,1,(0,0,255),1) """
                        """ if point_count < 20:
                            point_count += 1
                            points_x.append(framemid_x)
                            points_y.append(framemid_y)
                        elif point_count >= 20:
                            point_count = 0
                            points_x.clear()
                            points_y.clear()
                        if points_x :
                            poly = np.polyfit(points_x , points_y , 2)
                            for i , (posX,posY) in enumerate(zip(points_x,points_y)):
                                pos = (posX,posY)
                                if i == 0:
                                    cv2.line(frame,pos,pos,(0,255,0),2)
                                else:
                                    cv2.line(frame,pos,(points_x[i-1],points_y[i-1]),(0,255,0),2)
                            if direction == "Right":
                                x_list = [item for item in range(current_bbox_frame[-1][0],640)]  
                                mid_desired_x = int((640 + current_bbox_frame[-1][0])/2)
                            elif direction == "Left":
                                x_list = [item for item in range(0,current_bbox_frame[-1][0])] 
                                mid_desired_x = int(current_bbox_frame[-1][0]/2)
                            for x in x_list:
                                y_prediction=int(np.polyval(poly,x))
                                y_p = np.poly1d(poly)
                                predicted_y = int(y_p(mid_desired_x))
                                #print(y_p(mid_desired_x))
                                cv2.circle(frame,(x,y_prediction),2,(255,0,255),cv2.FILLED)
                                cv2.circle(frame,(mid_desired_x,predicted_y),7,(0,0,255),cv2.FILLED) """
                        point_list = [(hitbox_midpointx,hitbox_midpointy),(framemid_x,framemid_y),(hitbox_midpointx-1,0)]
                        self.angle ,self.direction= self.get_angle(point_list)
                        Camera.Angle = self.angle
                        Camera.Direction = self.direction
                        #print(self.direction,self.angle)
                        cv2.line(frame,(hitbox_midpointx,hitbox_midpointy),(framemid_x,framemid_y),color = (255,255,255),thickness=2)          
                        if (x > hitbox_left and end_cord_x < hitbox_right) and (y > hitbox_up and end_cord_y < hitbox_down):
                            if ( yatay > 5) and ( dikey > 5):
                                #kilitlenme_bilgisi = self.telemetry_packager.Iha_kilitlenme_bilgi()
                                if start == 0:
                                    lock_on_started = telemetry_packager.Kilitlenme_başlangıç()
                                    #lock_on_started = True
                                    start = datetime.now()
                                    camera_on_flag_time = datetime.now()
                                    başlangıç_zamanı = Camera._GPS_Saati()
                                diff = (datetime.now() - start).seconds
                                if success == True:
                                        success = False
                                        Camera.Success = False
                                if diff == 2:
                                    kilitlenme =False
                                    
                                Camera.Time = diff 
                                if diff == 4:
                                    lock_on_finished = telemetry_packager.Kilitlenme_bitiş()
                                    hedef_merkez_x = int((x+x+w)/2)
                                    hedef_merkez_y = int((y+y+h)/2)
                                    #print(hedef_merkez_x,hedef_merkez_y)
                                    bitiş_zamanı = Camera._GPS_Saati()
                                    kilitlenme_sayısı = kilitlenme_sayısı +1 
                                    success = True
                                    Camera.Success = success
                                    kilitlenme = True
                                    start = 0
                                    #print("Kilitlenme Sayısı:{}".format(kilitlenme_sayısı))
   

                                cv2.putText(frame,text="{} saniye".format(diff),org=(20,30),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(0,255,0),thickness=1,lineType=cv2.LINE_AA)
                                prev_bbox_frame = current_bbox_frame.copy()
                                if success == True:
                                    ######Send Data#####
                                    lock_on = {"otonom_kilitlenme": 1}
                                    self.kilitlenme_bilgisi = lock_on_started | lock_on_finished | lock_on
                                    print(self.kilitlenme_bilgisi)
                                if kilitlenme == True:
                                    cv2.putText(frame,text="Locking Success!",org=(20,50),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(0,255,0),thickness=1,lineType=cv2.LINE_AA)
                                
                            else:
                                start = 0
                                kilitlenme = False
                        else:
                            start = 0
                            kilitlenme = False
                            
                            if x < hitbox_left  and y < hitbox_sideway_1_bound_y:
                                target_window_location = "LeftUp"
                            elif x < hitbox_left and y > hitbox_sideway_2_bound_y:
                                target_window_location = "LeftDown"
                            elif x < hitbox_left and (hitbox_sideway_1_bound_y < y <hitbox_sideway_2_bound_y):
                                target_window_location = "Left"
                            elif x > hitbox_right  and y < hitbox_sideway_1_bound_y:
                                target_window_location = "RightUp"
                            elif x > hitbox_right and y > hitbox_sideway_2_bound_y:
                                target_window_location = "RightDown"
                            elif x > hitbox_right and (hitbox_sideway_1_bound_y < y <hitbox_sideway_2_bound_y):
                                target_window_location = "Right"
                            elif hitbox_upper_bound_x_2 > x > hitbox_upper_bound_x_1 and y < hitbox_up :
                                target_window_location = "Up"
                            elif x < hitbox_upper_bound_x_1 and y < hitbox_up : 
                                target_window_location = "LeftUp"
                            elif x > hitbox_upper_bound_x_2 and y < hitbox_up:
                                target_window_location = "RightUp"
                            elif hitbox_upper_bound_x_2 > x > hitbox_upper_bound_x_1 and y > hitbox_down :
                                target_window_location = "Down"
                            elif x < hitbox_upper_bound_x_1 and  y > hitbox_down :
                                target_window_location = "LeftDown"
                            elif x > hitbox_upper_bound_x_2 and  y > hitbox_down :
                                target_window_location = "RightDown"
                else : 
                    start = 0
                    kilitlenme = False
                    target_window_location = None
                    if camera_on_flag_time != 0:
                        camera_on_flag_time2 = (datetime.now() - camera_on_flag_time ).seconds
                        print(camera_on_flag_time2)
                if camera_on_flag_time2 == 6 : 
                    camera_on_flag = False
                # Display the resulting frame
                t = time.time()-t0
                self.fpsArray.append(1/t)
                averageFPS = mean(self.fpsArray)
                cv2.putText(frame,'FPS:' + str(averageFPS)[:4], (510,20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 1, cv2.LINE_AA)
                #self.recorder.write(frame)
                del self.fpsArray[:-180]
                cv2.imshow('preview',frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    for i in range(3):
                        print("....CLOSING CAMERA in {} second ....".format(3-i))
                        time.sleep(1)
                    break
        # When everything done, release the capture
        self.cap.release()
        cv2.destroyAllWindows()

class TelemetryCreate():
            
    def __init__(self):
        self.iha_bilgiler = {"IHA_enlem":0 ,
                            "IHA_boylam":0,
                            "IHA_irtifa": 0,
                            "IHA_dikilme": 0,
                            "IHA_yonelme": 0,
                            "IHA_yatis": 0,
                            "IHA_hiz": 0,
                            "IHA_batarya": 0,
                            "IHA_otonom": 0,
                            "IHA_kilitlenme": 0,
                            "Hedef_merkez_X": 0,
                            "Hedef_merkez_Y": 0,
                            "Hedef_genislik": 0,
                            "Hedef_yukseklik": 0}
        
    def _GPS_Saati(self):
        time_format = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        splitted = time_format.split(":")
        splitted1 = splitted[2].split('.')
        self.gps_saat = {"saat":splitted[0],"dakika":splitted[1],"saniye":splitted1[0],"milisaniye":splitted1[1]}
        return self.gps_saat
    def Kilitlenme_başlangıç(self):
        time = self._GPS_Saati()
        self.lock_on_start = {"kilitlenmeBaslangicZamani":{"saat:{},dakika:{},saniye:{},milisaniye:{}".format(time["saat"],time["dakika"],time["saniye"],time["milisaniye"])}}
        return self.lock_on_start
    def Kilitlenme_bitiş(self):
        time = self._GPS_Saati()
        self.lock_on_finish = {"kilitlenmeBitisZamani":{"saat:{},dakika:{},saniye:{},milisaniye:{}".format(time["saat"],time["dakika"],time["saniye"],time["milisaniye"])}}
        return self.lock_on_finish
    def Iha_telemetri_bilgi(self,takım_numarası:int,iha_bilgiler:list):
        time = self._GPS_Saati()
        takım_numarası = {"takim_numarasi": takım_numarası}
        self.takım_numarasi = takım_numarası
        i = 0
        for key , value in self.iha_bilgiler.items() :
            self.iha_bilgiler[key] = iha_bilgiler[i]
            i=i+1
        self.telemetry_data = self.takım_numarasi | self.iha_bilgiler | self.gps_saat    
        print(self.telemetry_data)
    def Iha_kilitlenme_bilgi(self):
        global lock_on_started , lock_on_finished , lock_on
        if lock_on== True and lock_on_started == True :
            self.Kilitlenme_başlangıç()
            process = True
            return process
        elif lock_on == True and lock_on_finished == True:
            lock_on = {"otonom_kilitlenme": 1}
            self.Kilitlenme_bitiş()
            self.kilitlenme_bilgisi = self.lock_on_start | self.lock_on_finish | lock_on
            return self.kilitlenme_bilgisi
        elif lock_on == False or lock_on_started == False or lock_on_finished == False:
            process = False
            return process

class Categorize():
    def __init__(self,team_number:int):
        
        
        self.team_number = team_number
        self.count = 0
        self.corresponding_enemy_list = []
        self.enemy_list = []
        self.is_initialized = False
        self.prev_list_initialized = False
        self.on_loop = False
        self.sorted_list_counter = 0
        self.characteristic_list = []

    def create_decision(self):
        global data , incoming_request , incoming_altitude , incoming_latitude , incoming_longitude , incoming_enemy_id,incoming_distance
        while True:
            if data != 0:
                incoming_request = data["incoming_request"]
                incoming_altitude = data["incoming_altitude"]
                incoming_latitude = data["incoming_latitude"]
                incoming_longitude = data["incoming_longitude"]
                incoming_enemy_id = data["incoming_enemy_id"]
                incoming_distance = data["incoming_distance"] 

            #print(incoming_request,incoming_distance)
            Camera_angle = Camera.Angle
            In_camera_direction = Camera.Direction
            lock_on_flag = Camera.Success

                            
            #DÜZENLE OPTİMİZE ET UÇAKLAR İÇİN FRONT BEHİND İÇİN AYRICA BİR DE YANINA SEÇENEĞİ GETİR
            #print(Camera_angle,In_camera_direction,lock_on_flag)
        return True


def uav_server():
        global data
        hostname=socket.gethostname()   
        IPAddr=socket.gethostbyname(hostname) 
        host_uav = IPAddr  
        #host_uav ="192.168.1.27"
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
            
                data = conn.recv(2048)
                data = pickle.loads(data) 
                print(data)
                if data_prev != data:
                    if type(data) == list:
                        #behaivour_dict=drive.flight_controller(incoming_data=data)
                        data_prev = data
                
                time.sleep(0.807)
                if not data:
                    # if data is not received break
                    break 
                print("Incoming Ground Control Station Data")


        conn.close()  # close the connection

def pixhawk_runtime():
    global mode , camera_on_flag , cruise_angle_deg , a , incoming_attitude_list , incoming_direction,target_window_location 
    count4 = 0
    global pitch_cam_angle , roll_cam_angle
    global landed
    default_pitch_val_temp = default_pitch_val
    default_pitch_val_temp2 = default_pitch_val
    land_flag = False
    i=0 
    while True:

        if incoming_request == "Fight":
            if  plane.vehicle.battery.level < 80 and landed == False:
                    land_flag = True
                    plane.set_ground_course(plane.att_heading_deg, plane.pos_alt_rel)
                    time.sleep(0.1)
                    plane.send_to_landing_point()
                    #plane.set_ap_mode("GUIDED")
                    if plane.home_landing_heading_angle > 180:
                        angle = plane.home_landing_heading_angle - 180
                    else : 
                        angle = plane.home_landing_heading_angle + 180
                    print("Landing angle is {}".format(angle))
                    #plane.set_ground_course(angle,60)
                    #time.sleep(1)
                    turn_flag = False
                    plane.set_airspeed(14)
                    land_mission = Command(0,0,0,3,21,0,0,0,0,0,angle,plane.location_home.lat,plane.location_home.lon,0)
                    plane.mission.add(land_mission)
                    plane.vehicle.flush()
                    time.sleep(2)
                    plane.set_ap_mode("AUTO")
                    while plane.location_current.alt >= 1:
                        if plane.get_ap_mode() == "RTL":
                            plane.set_ap_mode("AUTO")
                        #mavutil.mavlink.MAV_CMD_NAV_LAND = 21
                        print("Plane is descending")
                        time.sleep(0.2)
                        cmd_set = False
                    if plane.location_current.alt <= 1:
                        plane.set_airspeed(0)
                        plane.set_ap_mode("MANUAL")
                        landed = True
                        if plane.is_armed() :
                            """ disarm_cmd = plane.vehicle.message_factory.command_long_send(0,0,400,0,0,0,0,0,0,0,0)
                            plane.vehicle.send_mavlink(disarm_cmd) """
                            print("Disarmed")
                            plane.disarm()
                        
                        print("Landing complete")
            if not camera_on_flag and land_flag == False:
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
                    
                    aas = [(39.8575735,32.7880096),(39.8570464,32.8010559),(39.8474262,32.8091240)]
                    roll_val  = default_roll_val
                    plane.clear_mission()
                    
                    
                    target_location = LocationGlobalRelative(aas[i][0],aas[i][1],incoming_altitude)
                    i = i + 1
                    if i == 2:
                        i = 0
                    #target_location=LocationGlobalRelative(incoming_latitude,incoming_longitude,incoming_altitude)
                    #message = Command(0,0,0,mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,0,0,0,5,0,0,incoming_latitude,incoming_longitude,incoming_altitude)
                    #plane.vehicle.send_mavlink(message)
                    plane.goto(target_location)
                    time.sleep(3)
                    #plane.clear_mission()
            elif camera_on_flag and land_flag == False:
                if target_window_location != None : 
                    print(target_window_location)
                #plane.clear_mission()
                plane.set_ap_mode("GUIDED")
                roll , pitch , yaw = 0,0,0
                if target_window_location != None:
                    plane.set_airspeed(25)
                    if "Left" in target_window_location :
                        roll_val = 1420
                        roll = -20
                        pitch = 0
                    if "Right" in target_window_location :
                        roll_val = 1580
                        roll= 20
                        pitch = 0
                    if "Up" in target_window_location:
                        default_pitch_val_temp = default_pitch_val_temp + 20
                        pitch = 10
                    if "Down" in target_window_location: 
                        pitch = -10
                        default_pitch_val_temp2 = default_pitch_val_temp - 20
                    else:
                        default_pitch_val_temp = default_pitch_val
                        default_pitch_val_temp2 = default_pitch_val
                    #plane.send_set_attitude_target(roll,pitch,yaw)
                    plane.send_set_attitude_target(roll_cam_angle,pitch_cam_angle,yaw)
                    time.sleep(0.3)
                    if target_window_location is None :
                        plane.clear_all_rc_override()

                    
        elif incoming_request == "GPS":
            pass  
        elif incoming_request == "Escape":
            pass
        elif incoming_request == "Kamikaze":
            pass
        elif incoming_request == "RTL":
            pass
        elif incoming_request == "Land":
            plane.send_to_landing_point()
            while plane.location_current.alt > 1:
                plane.set_ap_mode("AUTO")
                plane.clear_mission()
                land_mission = Command(0,0,0,3, mavutil.mavlink.MAV_CMD_NAV_LAND,0,0,0,0,0,0,plane.location_home.lat,plane.location_home.lon,plane.location_home.alt)
                plane.mission.add(land_mission)
                plane.vehicle.flush()
                print("Plane is descending")
                cmd_set = False
            if plane.location_current.alt < 1:
                plane.set_ap_mode("MANUAL")
                plane.set_airspeed(0)
                landed = True
                plane.disarm()
                print("Landing complete")

        elif incoming_request == "Takeoff":
            plane.arm_and_takeoff()#Default to 50 meter altitude
        elif incoming_request == "Guided":
            plane.set_ap_mode("GUIDED")         
        elif incoming_request == "Loiter":
            plane.set_ap_mode("LOITER")      
        elif incoming_request == "Manual":
            plane.clear_all_rc_override()
            plane.clear_mission()
            while incoming_request == "Manual":
                pass
        """ while True:
            target_location=LocationGlobalRelative(lat=target_lat,lon=target_lon,alt=target_alt)
            plane.goto() """
if __name__ == "__main__":
    
    #start = datetime.now()
    telemetry_packager = TelemetryCreate()
    drive = Categorize(team_number=team_number)
    drive_thread = threading.Thread(target=drive.create_decision)
    drive_thread.start()
    camera = Camera()
    camerathread = threading.Thread(target=camera.detect)
    #camerathread.setDaemon(True)
    camerathread.start()
    thread1 = threading.Thread(target=uav_server)
    thread1.start()
    parser = argparse.ArgumentParser()
    parser.add_argument('--connect', default='tcp:127.0.0.1:5762')
    args = parser.parse_args()
    connection_string = args.connect
    #-- Create the object
    plane = Plane(connection_string)
    while incoming_request != "Proceed":
        print("Waiting for proceed command")
        time.sleep(1)
    #-- Arm and takeoff
    if not plane.is_armed(): plane.arm_and_takeoff()
    time.sleep(5)
    #-- Set in Guided and test the ground course
    plane.set_ap_mode("GUIDED")
    a = 0 ###TEMP DELETE LATER
    incoming_direction = "Turn Right"
    plane.set_rc_channel(4,default_pitch_val)
    pixhawk_thread = threading.Thread(target=pixhawk_runtime)
    pixhawk_thread.start()
    #print(datetime.now() - start)
    
        


    

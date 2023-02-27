import tkintermapview,math,sys,threading,socket,selectors,time,pickle,traceback,tkinter
import tkinter,socket, pickle,tkintermapview,os,socket,sys,selectors,traceback,threading,sys,time,math,geopy.distance,cv2
sys.path.insert(1, r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\src\modules')
import telemetry_data
import libclient
from threading import Timer 
from collections import defaultdict
from numpy import mean
import numpy as np
from PIL import ImageTk, Image
from pyproj import Geod
from math import sin, cos, sqrt, atan2, radians ,acos ,degrees,atan,asin
from datetime import datetime
from geographiclib.geodesic import Geodesic
from scipy.interpolate import *
from sklearn.preprocessing import PolynomialFeatures,StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
import TelemetryLibServer
#import matplotlib.pyplot as plt
######TX Variables#########
incoming_roll = 1500
incoming_yaw = 1500
incoming_pitch = 1500
incoming_altitude = 0
incoming_latitude = 0
incoming_long = 32.78342
incoming_enemy_id = 0
incoming_distance = 0
incoming_request = 0
incoming_longitude = 0
incoming_wait_ready_request = 0
tx_data = defaultdict(list)
point_to_track = {"enemy_id":0,"predicted_lat":0,"predicted_lon":0}
plane_to_track = 0
in_range_list = [-1,-1,-1]
#GUI Parameters
otonom_kalkış_cmd = False  
otonom_iniş_cmd = False  
Manual_cmd = False  
kamikaze_cmd = False  
otonom_it_dalaşı_cmd = False 
loiter_cmd = False 
guided_cmd = False
rtl_cmd= False
sel = 0
start = 0
start2 = 0
in_waiting = False
our_telemetry = 0
window_initialized = False
prev_drawing = []
drawing_initialized = False
waiting_data_to_draw = False
mode_1  = "Otonom"
mode_2 = "Manuel"
mode = "Otonom"
locking_count = 0
transmit_stopped = False
transmit_start = False
mission_start = False
client_socket_uav = 0
message_ready = False
#Localizasyon Parameters
Latitude_pts = []
Longitude_pts = []
Altitude_pts = []
enemy_list  = 0
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
host = "127.0.0.1"
hostname=socket.gethostname()   
IPAddr=socket.gethostbyname(hostname) 
uav_host = IPAddr
uav_port = 65433
port = 65432

class ServerConnection:
    def create_post_value(value):
        request_post = {
        "/api/telemetri_gonder":telemetry_data.telemetry_data,
        "/api/kilitlenme_bilgisi":telemetry_data.lock_on_data,
        "/api/giris":telemetry_data.login,
        "/api/kamikaze_bilgisi":telemetry_data.kamikaze_list,
        }
        sent = request_post[value]
        return  sent
    def create_request(action, value):
        if action == 'post':
            sent = ServerConnection.create_post_value(value=value)
        else:
            sent = "Nothing sent"
        if action == "get" or action == "post":
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, value=value ,sent = sent ),
            )
        else:
            return dict(
                type="binary/custom-client-binary-type",
                encoding="binary",
                content=bytes(action + value + sent, encoding="utf-8"),
            )

    

    def start_connection(host, port,action, request):
        global sel
        addr = (host, port)
        print(f"Starting connection to {addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(addr)
        sock.setblocking(False)
        sock.connect_ex(addr)
        sel = selectors.DefaultSelector()
        events =  selectors.EVENT_READ | selectors.EVENT_WRITE
        message = libclient.Message(sel, sock, addr, request)
        sel.register(sock, events, data=message)


class Categorize():
    def __init__(self,team_number:int):
        self.localization = Localization()
        self.team_number = team_number
        self.count = 0
        self.corresponding_enemy_list = []
        self.enemy_list = []
        self.is_initialized = False
        self.prev_list_initialized = False
        self.on_loop = False
        self.sorted_list_counter = 0
        self.characteristic_list = []
    def new_location_set(self,distance,angle,location:list,lat_change,lon_change,rotation):
        EARTH_RADIUS_IN_METER = 6378160
        EARTH_RADIUS_IN_KM = 6378.137
        global z
        
        distance_lat = distance * cos(72)
        distance_lon = distance * sin(72)
        if z == 1:
            distance_lat = distance * cos(18)
            distance_lon = distance * sin(18)
        if z == 2:
            z =0
        pi = math.pi
        m = (1 / ((2 * pi / 360) * EARTH_RADIUS_IN_KM)) / 1000;  #1 meter in degree
        if lat_change <=0 and lon_change <= 0:
            new_latitude = location[0] + (distance_lat * m)
            new_longitude = location[1] + (distance_lon * m) / cos(location[0] * (pi / 180))
        elif lat_change >=0 and lon_change >= 0:
            new_latitude = location[0] - (distance_lat * m)
            new_longitude = location[1] - (distance_lon * m) / cos(location[0] * (pi / 180))
            if rotation >225:
                new_latitude = location[0] + (distance_lat * m)
                new_longitude = location[1] - (distance_lon * m) / cos(location[0] * (pi / 180))
        elif lat_change <=0 and lon_change >= 0:
            new_latitude = location[0] + (distance_lat * m)
            new_longitude = location[1] - (distance_lon * m) / cos(location[0] * (pi / 180))
        elif lat_change >=0 and lon_change <= 0:
            new_latitude = location[0] - (distance_lat * m)
            new_longitude = location[1] + (distance_lon * m) / cos(location[0] * (pi / 180))
        z = z +1
        return [new_latitude,new_longitude]
    
    def distance_sort(self):
        """Sorts distances from enemy list 

        Returns:
            list: Sorted distance list ascending
        """
        c = 0
        distance_list = []
        sorted_distance_list = [1,2,3]
        for i in range(len(self.corresponding_enemy_list)):
            distance_list.append(0)
        for enemy in self.corresponding_enemy_list:
            if enemy != [] and enemy[-1]["enemy_id"] != self.team_number:
                distance_list[c]= {"enemy_id":enemy[0]["enemy_id"],"horizantal_distance":enemy[0]["horizantal_distance"]}
                #distance_list[c]= {"enemy_id":{"enemy_id":enemy[0]["enemy_id"],"horizantal_distance": enemy[0]["horizantal_distance"]} }
            else:
                distance_list[c] = {}
                index_number = c
            c = c+1     
        if {} in distance_list:
            distance_list.pop(index_number)
        distance_list.sort(key=lambda x: int(str(int(x.get('horizantal_distance'))),0), reverse=False)
        for i in range(3):
            sorted_distance_list[i] = distance_list[i]
        return sorted_distance_list
    
        
    def polynomial_pred(self,lat , lon , ele,pred_time):
        SEED = 42
        time = np.linspace(1,5,50)
        time= np.reshape(time,(-1,1))
        lat = np.reshape(lat,(-1,1))
        lon = np.reshape(lon,(-1,1))
        x_train_time_lat, x_test_time_lat, y_train_lat, y_test_lat = train_test_split(time, lat, test_size=0.25, random_state=SEED)
        x_train_time_lon, x_test_time_lon, y_train_lon, y_test_lon = train_test_split(time, lon, test_size=0.25, random_state=SEED)
        poly_transform = PolynomialFeatures(degree=3, include_bias=False)
        x_poly_train_time_lat = poly_transform.fit_transform(x_train_time_lat)
        x_poly_test_time_lat = poly_transform.transform(x_test_time_lat)
        x_poly_train_time_lon = poly_transform.fit_transform(x_train_time_lon)
        x_poly_test_time_lon = poly_transform.transform(x_test_time_lon)
        regressor_lat = make_pipeline(StandardScaler(with_mean=False), LinearRegression())
        regressor_lat.fit(x_poly_train_time_lat, y_train_lat)
        regressor_lon = make_pipeline(StandardScaler(with_mean=False), LinearRegression())
        regressor_lon.fit(x_poly_train_time_lon, y_train_lon)
        y_pred_lat = regressor_lat.predict(poly_transform.fit_transform([[pred_time]]))
        y_pred_lon = regressor_lon.predict(poly_transform.fit_transform([[pred_time]]))
        return y_pred_lat,y_pred_lon,pred_time

    def polynomial_calc(self):
        polynomial_list = []
        time = [1,2,3,4,5]
        enlem_list = []
        boylam_list = []
        irtifa_list = []
        prediction_list = []
        prev_enlem = 0
        prev_boylam = 0
        global Latitude_pts , Longitude_pts , Altitude_pts
        
        for enemy in self.corresponding_enemy_list:
            enlem_list.clear()
            boylam_list.clear()
            irtifa_list.clear()
            res = 1.2 # interpolation resolution (in meters)
            deg = 3 # interpolation degree N (N = 1 for linear interpolation, 2 <= N <= 5 for spline interpolation)
            for plane in enemy:
                enlem_list.append(plane["Enlem"])
                boylam_list.append(plane["Boylam"])
                irtifa_list.append(plane["İrtifa"])
            lat , lon , ele = self.GPX_interpolate(enlem_list,boylam_list,irtifa_list,res=res,deg = deg)
            for i in range(len(enlem_list)):
                polynomial_list.append([enlem_list[i],boylam_list[i]])

            pred_lat_1sec,pred_lon_1sec,pred_time_1sec=self.polynomial_pred(lat,lon,ele,6)
            enlem_list.append(pred_lat_1sec)
            boylam_list.append(pred_lon_1sec)
            time.append(pred_time_1sec)
            prediction_list.append({"enemy_id":enemy[-1]["enemy_id"],"pred_lat_1sec":pred_lat_1sec,"pred_lon_1sec":pred_lon_1sec,"pred_time_1sec":pred_time_1sec})

        return prediction_list

    def GPX_interpolate(self,lat, lon, ele, res, deg):
        if not 1 <= deg <= 5:
            print('ERROR deg out of [1-5] range, skipping interpolation')
            return(lat, lon, ele)
        elif not len(lat) == len(lon) == len(ele) :
            print('ERROR data input size mismatch, skipping interpolation')
            return(lat, lon, ele)
        else:
            # calculate distance data
            dist = self.GPX_calculate_dist(lat, lon, ele)
            # calculate normalized cumulative distance
            dist_cum_norm = np.cumsum(dist)/np.sum(dist)
            # interpolate spatial data
            """ data = [lat, lon, ele]
            tck, _ = splprep(x = data, u = dist_cum_norm, k = int(deg), s = 0, nest = len(lat)+int(deg)+1)
            u_interp = np.linspace(0, 1, 50)
            out = splev(u_interp, tck)
            lat_interp = out[0]
            lon_interp = out[1]
            ele_interp = out[2] """
            lat_interp = np.linspace(min(lat), max(lat), 50) 
            lon_interp = np.linspace(min(lon), max(lon), 50) 
            ele_interp = np.linspace(min(ele), max(ele), 50) 
            # remove insignificant digits
            lat_interp = np.round(lat_interp*1e6)/1e6
            lon_interp = np.round(lon_interp*1e6)/1e6
            ele_interp = np.round(ele_interp*1e1)/1e1
        return(lat_interp, lon_interp, ele_interp)

    def GPX_calculate_dist(self,lat, lon, ele): # calculate distance between trackpoints
        dist = np.zeros(len(lat))
        EARTH_RADIUS_IN_METER = 6378160
        for i in np.arange(1, len(lat)):
            lat1 = np.radians(lat[i-1])
            lon1 = np.radians(lon[i-1])
            lat2 = np.radians(lat[i])
            lon2 = np.radians(lon[i])
            # haversine formula
            delta_lat = np.abs(lat2-lat1)
            delta_lon = np.abs(lon2-lon1)
            c = 2.0*np.arcsin(np.sqrt(np.sin(delta_lat/2.0)**2+np.cos(lat1)*np.cos(lat2)*np.sin(delta_lon/2.0)**2))
            dist_lat_lon = EARTH_RADIUS_IN_METER*c
            # calculate elevation change
            dist_ele = ele[i]-ele[i-1]
            dist[i] = np.sqrt(dist_lat_lon**2+dist_ele**2)
        return(dist)

    def check_collision(self,prediction_list):
        error_rate_list = []
        for prediction in prediction_list:
            if prediction["enemy_id"] == self.team_number:
                our_pred_lat , our_pred_lon,our_pred_time = prediction["pred_lat_1sec"],prediction["pred_lon_1sec"],prediction["pred_time_1sec"]
        for prediction in prediction_list:
            if prediction["enemy_id"] != self.team_number:
                collision_flag = False
                enemy_pred_lat , enemy_pred_lon,enemy_pred_time = prediction["pred_lat_1sec"],prediction["pred_lon_1sec"],prediction["pred_time_1sec"]
                our_lat_error_const = (our_pred_lat * (10**6)) % 1000
                our_lon_error_const = (our_pred_lon * (10**6)) % 1000
                our_time_error_const = (our_pred_time * (10**6)) % 1000
                enemy_lat_error_const = (enemy_pred_lat * (10**6)) % 1000
                enemy_lon_error_const = (enemy_pred_lon * (10**6)) % 1000
                enemy_time_error_const = (enemy_pred_time * (10**6)) % 1000
                lat_error_rate = (max(our_lat_error_const,enemy_lat_error_const) - min(our_lat_error_const,enemy_lat_error_const))/max(our_lat_error_const,enemy_lat_error_const)
                lon_error_rate = (max(our_lon_error_const,enemy_lon_error_const) - min(our_lon_error_const,enemy_lon_error_const))/max(our_lon_error_const,enemy_lon_error_const)
                #time_error_rate = (max(our_time_error_const,enemy_time_error_const) - min(our_time_error_const,enemy_time_error_const))/max(our_time_error_const,enemy_time_error_const)
                if lat_error_rate < 0.035 and lon_error_rate < 0.035:
                    collision_flag = True
                error_rate_list.append({"enemy_id":prediction["enemy_id"],"lat_error_rate":lat_error_rate,"lon_error_rate":lon_error_rate,"collision_flag":collision_flag})
        return error_rate_list

    def create_escape(self):
        characteristics_list = self.get_characteristics()
        in_range_count = 0
        global in_range_list
        base_angle = 0
        for enemy in self.corresponding_enemy_list:
            if enemy[-1]["enemy_id"] == self.team_number:
                base_angle = enemy[-1]["bearing_angle"]
            if enemy != [] and enemy[-1]["enemy_id"] != self.team_number:
                if enemy[-1]["where_is_enemy"] == 'Behind':
                    if enemy[-1]["alt_command"] == "Below":
                        alt_command = "Dive"
                    elif enemy[-1]["alt_command"] == "Above":
                        alt_command = "Rise"
                    if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("priority1") == True and characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("is_dangerous")== True:
                        speed = 75
                        if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("avoid_immediate") == True:
                            speed = 100
                        escape_angle= 90 + enemy[-1]["Qrotate"]
                        in_range_list[0]=[enemy[-1]["turn_direction_for_us"],escape_angle,alt_command,speed,enemy[-1]["enemy_id"]]
                        in_range_count = in_range_count + 1
                    elif characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("priority2") == True and characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("is_dangerous")== True:
                        speed = 75 
                        if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("avoid_immediate") == True:
                            speed = 100
                        escape_angle= 90 + enemy[-1]["Qrotate"]
                        in_range_count = in_range_count + 1
                        in_range_list[1]=[enemy[-1]["turn_direction_for_us"],escape_angle,alt_command,speed,enemy[-1]["enemy_id"]]
                    elif characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("priority3") == True and characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("is_dangerous")== True:
                        speed = 75
                        if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("avoid_immediate") == True:
                            speed = 100
                        escape_angle= 90 + enemy[-1]["Qrotate"]
                        in_range_count = in_range_count + 1
                        in_range_list[2]=[enemy[-1]["turn_direction_for_us"],escape_angle,alt_command,speed,enemy[-1]["enemy_id"]]
                    else : 
                        in_range_list = [0,0,0]
        if in_range_count == 1:
            for i in in_range_list:
                if i != 0:
                    print("Turn {} with angle {} at %{} speed from enemy_id : {}  \n".format(i[0],i[1],i[3],i[4]))
        elif in_range_count == 2:
            print("Slow down to the %10 speed and turn right")
        elif in_range_count == 3:
            print("Slow down to the %10 speed and turn right and dive")
        else:
            print("Continue Mission")
        self.enemy_list.clear()
        self.characteristic_list = characteristics_list
        return in_range_list , characteristics_list

    
    def gauss(self,x1, x2, y1, y2):
        """
        Apply a Gaussian kernel estimation (2-sigma) to distance between points.

        Effectively, this applies a Gaussian kernel with a fixed radius to one
        of the points and evaluates it at the value of the euclidean distance
        between the two points (x1, y1) and (x2, y2).
        The Gaussian is transformed to roughly (!) yield 1.0 for distance 0 and
        have the 2-sigma located at radius distance.
        """
        return (
            (1.0 / (2.0 * math.pi))
            * math.exp(
                -1 * (3.0 * math.sqrt((x1 - x2)**2 + (y1 - y2)**2) / self.radius))**2
            / 0.4)


    def _kde(self,x, y):
        """
        Estimate the kernel density at a given position.

        Simply sums up all the Gaussian kernel values towards all points
        (pts_x, pts_y) from position (x, y).
        """
        return sum([
            self.gauss(x, px, y, py)
            # math.sqrt((x - px)**2 + (y - py)**2)
            for px, py in zip(Latitude_pts, Longitude_pts)
        ])

    def create_route(self,prediction_list):
        global incoming_altitude , incoming_distance , incoming_latitude , incoming_longitude , incoming_enemy_id ,plane_to_track,point_to_track
        collision_flag = False
        point_list = []
        dummy_distance = 5000
        error_rate_list = self.check_collision(prediction_list)###########CHECK FOR COLLISONS
        for enemy in self.corresponding_enemy_list:
            if enemy[-1]["enemy_id"] == self.team_number:
                    us_enlem = enemy[-1]["Enlem"]
                    us_boylam = enemy[-1]["Boylam"]
        for enemy in self.corresponding_enemy_list:
            if enemy != [] and enemy[-1]["enemy_id"] != self.team_number:
                enemy_enlem = enemy[-1]["Enlem"]
                enemys_boylam = enemy[-1]["Boylam"]
                for collision in error_rate_list:
                    if collision["enemy_id"] == enemy[-1]["enemy_id"]:
                        if collision["collision_flag"] == True:
                            collision_flag = True
                if enemy[-1]['where_is_enemy'] == 'Front':
                    direction = enemy[-1]['turn_direction_for_us']
                    angle = enemy[-1]['Qtrack']
                    distance = enemy[-1]["horizantal_distance"]
                    if distance < dummy_distance:
                        plane_to_track = enemy[-1]["enemy_id"]
                        dummy_distance = distance
                    #Açıya göre yol parametresi çizimi yap
                for prediction in prediction_list:
                    if prediction["enemy_id"] == enemy[-1]["enemy_id"]:
                        if collision_flag == True:
                            collision_flag = False
                            point = self.collision_avoid([enemy[-1]["Enlem"],enemy[-1]["Boylam"]],enemy[-1]["lat_change"],enemy[-1]["lon_change"],prediction)
                            point = {"enemy_id":prediction["enemy_id"],"predicted_lat":point[0],"predicted_lon":point[1]}
                        else:
                            point = {"enemy_id":prediction["enemy_id"],"predicted_lat":prediction["pred_lat_1sec"],"predicted_lon":prediction["pred_lon_1sec"]}
                        if plane_to_track == enemy[-1]["enemy_id"] :
                            incoming_altitude = enemy[-1]["İrtifa"]
                            incoming_latitude = point["predicted_lat"]
                            incoming_longitude = point["predicted_lon"]
                            incoming_enemy_id = point["enemy_id"]
                            incoming_distance = enemy[-1]["horizantal_distance"]
                            point_to_track = point
                        point_list.append(point)
        return point_list , point_to_track
    
    def collision_avoid(self,location,lat_change,lon_change):
        EARTH_RADIUS_IN_KM = 6378.137
        distance = 5
        distance_lat = distance * cos(72)
        distance_lon = distance * sin(72)
        pi = math.pi
        m = (1 / ((2 * pi / 360) * EARTH_RADIUS_IN_KM)) / 1000;  #1 meter in degree
        if lat_change <=0 and lon_change <= 0:
            new_latitude = location[0] + (distance_lat * m)
            new_longitude = location[1] + (distance_lon * m) / cos(location[0] * (pi / 180))
        elif lat_change >=0 and lon_change >= 0:
            new_latitude = location[0] - (distance_lat * m)
            new_longitude = location[1] - (distance_lon * m) / cos(location[0] * (pi / 180))
        elif lat_change <=0 and lon_change >= 0:
            new_latitude = location[0] + (distance_lat * m)
            new_longitude = location[1] - (distance_lon * m) / cos(location[0] * (pi / 180))
        elif lat_change >=0 and lon_change <= 0:
            new_latitude = location[0] - (distance_lat * m)
            new_longitude = location[1] + (distance_lon * m) / cos(location[0] * (pi / 180))
        z = z +1
        return [new_latitude,new_longitude]

    def get_characteristics(self) ->dict:
        """From all gps inputs it is checking all planes for 
        if they are closing on us or not and returning an boolean dictionary

        is_approaching : True means a plane is closing the distance between us
        is_watching : True means this plane is entered for watchzone area
        is_in_watchlist : True means this plane is in now possible threats
        is_dangerous : True means there is a follower on us bail out
        avoid_immediate : True means avoiding is first thing to consider 
        priority1: If this flag exist in any enemy_id that enemy is the first priority
        priority2: If this flag exist in any enemy_id that enemy is the second priority
        priority3: If this flag exist in any enemy_id that enemy is the third priority
        Returns:
            dict: Boolean Dictionary filled with condition flags
        """
        priority_attached_list = []
        behaviour_dict = {}
        c = 0
        is_approaching = False
        is_watching = False
        is_in_watch_list = False
        is_dangerous = False
        avoid_immediate = False
        sorted_distance_list = self.distance_sort()
        global prev_distance_list
        global counter
        if self.prev_list_initialized == False:
            for enemy in self.corresponding_enemy_list:
                if enemy != []:
                    prev_distance_list = prev_distance_list |  {"enemy_id{}".format(enemy[0]["enemy_id"]):enemy[0]["horizantal_distance"]}
            self.prev_list_initialized = True
        for enemy in self.corresponding_enemy_list:  
            horizantal_angle_change = 0
            total_angle_change = 0
            horizantal_distance_change = 0 
            
            if enemy != [] and enemy[-1]["enemy_id"] != self.team_number:
                
                if enemy[-1] != 0 :
                    horizantal_angle_change = enemy[-1]["bearing_angle"] - horizantal_angle_change
                    """ total_angle_change = enemy[-1]["total_angle"] - total_angle_change """
                    horizantal_distance_change = enemy[-1]["horizantal_distance"] - prev_distance_list["enemy_id{}".format(enemy[-1]["enemy_id"])]
                    prev_distance_list["enemy_id{}".format(enemy[-1]["enemy_id"])] = enemy[-1]["horizantal_distance"]
                    line_rotation_right = enemy[-1]["bearing_angle"]+32
                    line_rotation_left = enemy[-1]["bearing_angle"]-32
                    right_line=self.new_location_set(distance=80,angle=line_rotation_right,location=[enemy[-1]["Enlem"],enemy[-1]["Boylam"]],
                                                     lat_change=enemy[-1]["lat_change"],lon_change=enemy[-1]["lot_change"],
                                                     rotation=enemy[-1]["bearing_angle"])
                    left_line=self.new_location_set(distance=80,angle=line_rotation_left,location=[enemy[-1]["Enlem"],enemy[-1]["Boylam"]],
                                                    lat_change=enemy[-1]["lat_change"],lon_change=enemy[-1]["lot_change"],
                                                    rotation=enemy[-1]["bearing_angle"])
                
                if enemy[-1]["where_is_enemy"] == "Front":
                    is_approaching = True
                    if horizantal_distance_change >0:
                        is_approaching = False
                    is_watching = False
                    is_in_watch_list = False
                    is_dangerous = False
                    avoid_immediate = False
                if enemy[-1]["where_is_enemy"] == "Behind":
                        is_approaching = True
                        if horizantal_distance_change >0:
                            is_approaching = False
                        if enemy[-1]["where_is_enemy"] == "Behind":
                            if enemy[-1]["Qrotate"] <45 and enemy[-1]["Qrotate"] >-45:
                                if enemy[-1]["horizantal_distance"] < 50:    
                                    is_dangerous = True
                                    is_watching = True
                                    is_in_watch_list = True
                                    avoid_immediate = True
                                elif enemy[-1]["horizantal_distance"] < 80:
                                    is_dangerous = True
                                    is_watching = True
                                    is_in_watch_list = True
                                    avoid_immediate = False
                                else : 
                                    is_watching = True
                                    is_in_watch_list = True
                            elif enemy[-1]["Qrotate"] <15 and enemy[-1]["Qrotate"] >-15:
                                if enemy[-1]["horizantal_distance"] < 80:    
                                    is_dangerous = True
                                    is_watching = True
                                    is_in_watch_list = True
                                    avoid_immediate = True
                                else : 
                                    is_watching = True
                                    is_in_watch_list = True
                                    is_dangerous = True
                temp_dict = {"is_approaching":is_approaching,"is_watching":is_watching,"is_in_watch_list":is_in_watch_list,"is_dangerous":is_dangerous,"avoid_immediate":avoid_immediate,"right_line":right_line,"left_line":left_line}
                if self.sorted_list_counter <= 2 :
                        if enemy[-1]["enemy_id"] == sorted_distance_list[self.sorted_list_counter]["enemy_id"]:
                            
                            if self.sorted_list_counter == 0:
                                temp2_dict = {"priority1":True ,"priority2":False,"priority3":False}
                                temp3_dict = temp_dict | temp2_dict
                                priority_attached_list.append(enemy[-1]["enemy_id"])
                            elif self.sorted_list_counter == 1:
                                temp2_dict = {"priority1":False ,"priority2":True,"priority3":False }
                                temp3_dict = temp_dict | temp2_dict
                                priority_attached_list.append(enemy[-1]["enemy_id"])
                            elif self.sorted_list_counter == 2:
                                temp2_dict = {"priority1":False ,"priority2":False,"priority3":True }
                                temp3_dict = temp_dict | temp2_dict
                                priority_attached_list.append(enemy[-1]["enemy_id"])
                            behaviour_dict["enemy_id{}".format(enemy[-1]["enemy_id"])] = temp3_dict
                            self.sorted_list_counter = self.sorted_list_counter +1
                        else : 
                            behaviour_dict["enemy_id{}".format(enemy[-1]["enemy_id"])] = temp_dict   
                else:
                        behaviour_dict["enemy_id{}".format(enemy[-1]["enemy_id"])] = temp_dict
            c = c+1
        c = 0
        counter = counter + 1
        for info in sorted_distance_list:
            if info["enemy_id"] not in priority_attached_list:
                l = 0
                for k in sorted_distance_list:
                    if info["enemy_id"] == k["enemy_id"]:
                        priority_config_index = l
                        priority_attached_list.append(l)
                        break
                    l = l +1
                if priority_config_index == 0:
                    temp2_dict = {"priority1":True ,"priority2":False,"priority3":False }
                elif priority_config_index == 1:
                    temp2_dict = {"priority1":False ,"priority2":True,"priority3":False }
                elif priority_config_index == 2:
                    temp2_dict = {"priority1":False ,"priority2":False,"priority3":True }
                behaviour_dict["enemy_id{}".format(info["enemy_id"])] = behaviour_dict["enemy_id{}".format(info["enemy_id"])] | temp2_dict
                if len(priority_attached_list) == 3:
                    break
            c = c+1
        return behaviour_dict
    
        
        
    def create_decision(self,point_to_track):
        global tx_data,incoming_request ,incoming_wait_ready_request,incoming_attitude,incoming_longitude,incoming_altitude,incoming_latitude,incoming_enemy_id,incoming_distance 
        global in_range_list ,mission_start,message_ready,client_socket_uav
        global rtl_cmd,escape_cmd,guided_cmd,loiter_cmd,Manual_cmd,kamikaze_cmd,otonom_iniş_cmd,otonom_kalkış_cmd,otonom_it_dalaşı_cmd
        startup_flag = False
        
        print(in_range_list,point_to_track)
        if mission_start == False:
            startup_flag = False
            if in_range_list[0] == -1 or in_range_list[1] == -1 or in_range_list[2] == -1: 
                startup_flag = True 
                if mission_start == True:
                    mission_start = False
                    incoming_request = "Proceed"
            elif in_range_list[0] != 0 or in_range_list[1] != 0 or in_range_list[2] != 0 :
                escape_cmd = True
                incoming_request = "Escape"
            else:
                incoming_request = "Fight"
                escape_cmd = False 
                if kamikaze_cmd == True:
                    incoming_request = "Kamikaze"
                    kamikaze_cmd = False
                elif rtl_cmd == True :
                    incoming_request = "RTL"
                    rtl_cmd = False
                elif otonom_iniş_cmd == True:
                    incoming_request = "Land"
                    otonom_iniş_cmd = False
                elif otonom_it_dalaşı_cmd == True:
                    incoming_request = "Fight"
                    otonom_it_dalaşı_cmd = False
                elif otonom_kalkış_cmd == True:
                    incoming_request == "Takeoff"
                    otonom_kalkış_cmd = False
                elif guided_cmd == True:
                    incoming_request == "Guided"
                    guided_cmd = False
                elif loiter_cmd == True:
                    incoming_request = "Loiter"
                    loiter_cmd = False
                elif Manual_cmd == True:
                    incoming_request == "Manual"
                    Manual_cmd = False
                incoming_attitude = None
        if mission_start:
            startup_flag = True
            mission_start = False
            incoming_request = "Proceed"
        if startup_flag == False:
            tx_data = {"incoming_request":incoming_request,"incoming_altitude":incoming_altitude,"incoming_latitude":incoming_latitude,"incoming_longitude":incoming_longitude,"incoming_distance":incoming_distance,"incoming_enemy_id":incoming_enemy_id}
        elif startup_flag == True:
            startup_flag = False
            tx_data = {"incoming_request":incoming_request,"incoming_altitude":incoming_altitude,"incoming_latitude":incoming_latitude,"incoming_longitude":incoming_longitude,"incoming_distance":incoming_distance,"incoming_enemy_id":incoming_enemy_id}    
        message_ready = True
        if message_ready == True:
            time.sleep(0.05)
            tx_data = pickle.dumps(tx_data)
            client_socket_uav.send(tx_data)  # send message
            received_response = client_socket_uav.recv(2048)
            received_response = pickle.loads(received_response)
            print(received_response)
        return tx_data    

    def flight_controller(self):
        global previous_location_list
        global k
        global tx_data
        global enemy_list,in_range_list,point_list
        if enemy_list == 0:  
            print("waiting for correct data")
        if enemy_list != 0 and type(enemy_list) == list:
            incoming_data = enemy_list[0] #This is for fake server fix it later
            if not self.is_initialized:
                for i in incoming_data:
                    if i["takim_numarasi"] == self.team_number:
                        our_enlem=i["IHA_enlem"]
                        our_boylam=i["IHA_boylam"]
                        our_irtifa=i["IHA_irtifa"]
                        us = [our_enlem,our_boylam,our_irtifa]
                    self.enemy_list.append(i)
                if self.on_loop == False :
                    for a in range(len(self.enemy_list)+1):
                        self.corresponding_enemy_list.append([])
                    self.on_loop = True
                previous_location_list = incoming_data
                self.is_initialized = True 
            team_count = 0
            for enemy in incoming_data:
                if enemy["takim_numarasi"] == self.team_number:
                    our_enlem=enemy["IHA_enlem"]
                    our_boylam=enemy["IHA_boylam"]
                    our_irtifa=enemy["IHA_irtifa"]
                    us = [our_enlem,our_boylam,our_irtifa]
                team_count = team_count + 1
            for enemy in incoming_data:
                for prev_enemy in previous_location_list:
                        if prev_enemy["takim_numarasi"] == enemy["takim_numarasi"] :
                            prev_enlem=prev_enemy["IHA_enlem"]
                            prev_boylam=prev_enemy["IHA_boylam"]
                            prev_irtifa=prev_enemy["IHA_irtifa"]
                        if prev_enemy["takim_numarasi"] == self.team_number:
                            us_prev_enlem=prev_enemy["IHA_enlem"]
                            us_prev_boylam=prev_enemy["IHA_boylam"]
                            us_prev_irtifa=prev_enemy["IHA_irtifa"]
                            us_prev = [us_prev_enlem,us_prev_boylam,us_prev_irtifa]
                
                horizontal_difference ,bearing_angle ,alt_command,uDirection,lat_change,lon_change,self.enemy, rakip_irtifa ,diff_irtifa,Qrotate,Qtrack,turn_direction_for_enemy,turn_direction_for_us,where_is_enemy=self.localization.angle_calc(us=us,us_prev=us_prev,prev_enlem=prev_enlem,prev_boylam=prev_boylam,prev_irtifa=prev_irtifa,rakip_enlem= enemy["IHA_enlem"],rakip_boylam= enemy["IHA_boylam"],rakip_irtifa= enemy["IHA_irtifa"])
                result_listed={"enemy_id":enemy["takim_numarasi"],"Enlem":self.enemy[0],"Boylam":self.enemy[1],
                                "İrtifa":rakip_irtifa,"İrtifa_Farkı":diff_irtifa,"bearing_angle":bearing_angle, 
                                "horizantal_distance":horizontal_difference,"lat_change":lat_change,
                                "lot_change":lon_change,"alt_command":alt_command,"Plane_Direction":uDirection,
                                "Qrotate":Qrotate,"Qtrack":Qtrack,"turn_direction_for_enemy":turn_direction_for_enemy,
                                "turn_direction_for_us":turn_direction_for_us,"where_is_enemy":where_is_enemy}
                self.corresponding_enemy_list[enemy["takim_numarasi"] - 1].append(result_listed)
                global count
                count = count +1
            var=(team_count * 4) + 1
            prediction_list = 0
            if count >= var:
                prediction_list = self.polynomial_calc()
                for t in range(team_count):
                    self.corresponding_enemy_list[t].pop(0)
                count = (team_count * 4)
            k = k +1   
            #print(k)
            previous_location_list = incoming_data 
            b = 0
            check_flag = []
            for i in self.corresponding_enemy_list:
                if b !=0 and i == check_flag:
                    del self.corresponding_enemy_list[b:]
                    break
                b = b+1
            if prediction_list != 0:
                point_list ,point_to_track = self.create_route(prediction_list)
                in_range_list , characteristics_list = self.create_escape()
            if prediction_list == 0:
                point_to_track = {"enemy_id":0,"predicted_lat":0,"predicted_lon":0}
            tx_data = self.create_decision(point_to_track)

            return [self.corresponding_enemy_list]    
    

class Localization():
    """Calculates necessary angles , directions , x and y coordinates , 
       altitude differences between 1 plane with other planes in a given set 
       which consists of telemetry datas.
    """
    def __init__(self):
        self.R = 6373.0
        self.p0 = {"lat":39.860153,"lng":32.773298}
        self.p1=  {"lat":39.844360,"lng":32.793870}
        self.z1 = (39.860948, 32.770010)
        self.z2 = (39.864205,32.788550)
        self.z3 = (39.844797, 32.781285)
        self.z4 = (39.853096, 32.806683)
        self.estimation_initialized = False

    def get_bearing_angle(self,location:list,location_prev:list):
        brng = Geodesic.WGS84.Inverse(location_prev[0], location_prev[1], location[0], location[1])['azi1']
        delta_longitude = (location_prev[1]-location[1])
        y = sin(delta_longitude) * cos(location[0])
        x = (cos(location_prev[0]) * sin(location[0])) - (sin(location_prev[0]) * cos(location[0]) * cos(delta_longitude))
        bearing = atan2(y,x)
        bearing=math.degrees(bearing)
        bearing = (bearing +360) % 360
        return brng

    def angle_calc(self,us:list,us_prev:list,prev_enlem:float,prev_boylam:float,prev_irtifa:float,rakip_enlem:float,rakip_boylam:float,rakip_irtifa:int):
        """Calculates horizantal and total angle differences for two vector in 3D space.

        Args:
            enlem (float): Base latitude
            boylam (float): Base longitude
            irtifa (float): Base altitude
            rakip_enlem (float): Target's latitude
            rakip_boylam (float): Target's longitude
            rakip_irtifa (int): Target's altitude

        Returns:
            float: Angle values
        """
        self.prev_enemy = (prev_enlem,prev_boylam)
        self.enemy = (rakip_enlem,rakip_boylam)
        self.us =  (us[0],us[1])
        self.us_prev = (us_prev[0],us_prev[1])
        horizontal_difference=geopy.distance.geodesic(self.enemy, self.us).meters
        horizontal_difference_prev=geopy.distance.geodesic(self.prev_enemy, self.us_prev).meters
        distance_change = horizontal_difference_prev - horizontal_difference
        if self.estimation_initialized == False:
            
            self.estimation_initialized = True

        bearing_angle = self.get_bearing_angle(self.enemy,self.prev_enemy)
        our_bearing_angle = self.get_bearing_angle(self.us,self.us_prev)
        if bearing_angle < 0 :
            bearing_angle = bearing_angle * -1
        if our_bearing_angle < 0:
            our_bearing_angle = our_bearing_angle * -1
        Qrotate= bearing_angle - our_bearing_angle
        Qtrack = our_bearing_angle - bearing_angle
        uDirection = None
        ourDirection = None
        turn_direction_for_enemy = None
        turn_direction_for_us = None
        where_is_enemy = None
        diff_irtifa = rakip_irtifa - us[2]
        alt_command = None
        if bearing_angle <=90 and bearing_angle >=0:
            uDirection = "Q1"
        elif bearing_angle <=180 and bearing_angle >=90:
            uDirection = "Q4"
        elif bearing_angle <=270 and bearing_angle >=180:
            uDirection = "Q3"
        elif bearing_angle <=360 and bearing_angle >=270:
            uDirection = "Q2"
        if our_bearing_angle <=90 and our_bearing_angle >=0:
            ourDirection = "Q1"
        elif our_bearing_angle <=180 and our_bearing_angle >= 90:
            ourDirection = "Q4"
        elif our_bearing_angle <=270 and our_bearing_angle >=180:
            ourDirection = "Q3"
        elif our_bearing_angle <=360 and our_bearing_angle >=270:
            ourDirection = "Q2"
        
        margin = 0.001
        lat_diff = self.enemy[0]- self.us[0]
        long_diff = self.enemy[1] - self.us[1]
        if ourDirection == "Q1":
            if lat_diff > 0 and long_diff > 0:
                where_is_enemy = "Front"
            elif lat_diff > 0 and long_diff < 0:
                where_is_enemy = "Left"
            elif lat_diff <0 and long_diff > 0 :
                where_is_enemy = "Right"
            elif lat_diff < 0 and long_diff < 0:
                where_is_enemy = "Behind"
        elif ourDirection == "Q2":
            if lat_diff > 0 and long_diff > 0:
                where_is_enemy = "Right"
            elif lat_diff > 0 and long_diff < 0:
                where_is_enemy = "Front"
            elif lat_diff <0 and long_diff > 0 :
                where_is_enemy = "Behind"
            elif lat_diff < 0 and long_diff < 0:
                where_is_enemy = "Left"
        elif ourDirection == "Q3":
            if lat_diff > 0 and long_diff > 0:
                where_is_enemy = "Behind"
            elif lat_diff > 0 and long_diff < 0:
                where_is_enemy = "Right"
            elif lat_diff <0 and long_diff > 0 :
                where_is_enemy = "Left"
            elif lat_diff < 0 and long_diff < 0:
                where_is_enemy = "Front"
        elif ourDirection == "Q4":
            if lat_diff > 0 and long_diff > 0:
                where_is_enemy = "Left"
            elif lat_diff > 0 and long_diff < 0:
                where_is_enemy = "Behind"
            elif lat_diff <0 and long_diff > 0 :
                where_is_enemy = "Front"
            elif lat_diff < 0 and long_diff < 0:
                where_is_enemy = "Right"
        if diff_irtifa >0:
            alt_command = "Above"
        else:
            alt_command = "Below"
        if Qrotate > 180 and where_is_enemy == "Behind":
            Qrotate = Qrotate - 180
            turn_direction_for_enemy = "Right"
        elif (0<Qrotate and Qrotate< 180) and where_is_enemy == "Behind":
            turn_direction_for_enemy = "Left"
        elif Qrotate<0 and where_is_enemy == "Behind":
            turn_direction_for_enemy="Right"
        lat_change = rakip_enlem - prev_enlem
        lon_change = rakip_boylam - prev_boylam
        if distance_change <0:
            pass
        elif distance_change >0:
            if Qtrack > 180:
                Qtrack = Qtrack - 180
                turn_direction_for_us = "Right"
            elif 0<Qtrack and Qtrack< 180:
                turn_direction_for_us = "Left"
            elif Qtrack<0:
                turn_direction_for_us="Right"
        if Qtrack > 180:
                Qtrack = Qtrack - 180
                turn_direction_for_us = "Right"
        elif 0<Qtrack and Qtrack< 180:
                turn_direction_for_us = "Left"
        elif Qtrack<0:
                turn_direction_for_us="Right"
        error_rate_x ,error_rate_y= 10 , 10
        #prev_coordinates_enemylat_lon = [self.enemy,self.us]
        #Difference in total angle 
        #angle = ((enemy_x * us_x)+(enemy_y*us_y)+(rakip_irtifa*irtifa))/(sqrt((enemy_x ** 2)+(enemy_y ** 2)+(rakip_irtifa **2)) * sqrt((us_x ** 2)+(us_y ** 2)+(irtifa ** 2)))
        #angle_diff=math.degrees(acos(angle))
        return  horizontal_difference ,bearing_angle ,alt_command,uDirection , lat_change ,lon_change ,self.enemy , rakip_irtifa ,diff_irtifa,Qrotate,Qtrack,turn_direction_for_enemy,turn_direction_for_us,where_is_enemy

class Window(Categorize):
    @staticmethod
    def _dist(lat1, long1, lat2, long2):

        # convert decimal degrees to radians 
        lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])
        # haversine formula 
        dlon = long2 - long1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        # Radius of earth in meters is 6378160
        m = 6378160* c
        return m

    @staticmethod
    def _set_watch_points(distance,angle,location,lat_change,lon_change,rotation):
        EARTH_RADIUS_IN_METER = 6378160
        EARTH_RADIUS_IN_KM = 6378.137
        global p
        
        distance_lat = distance * cos(30)
        distance_lon = distance * sin(30)
        if p == 1:
            distance_lat = distance * cos(60)
            distance_lon = distance * sin(60)
        if p == 2:
            p =0
        pi = math.pi
        m = (1 / ((2 * pi / 360) * EARTH_RADIUS_IN_KM)) / 1000;  #1 meter in degree
        if lat_change <0 and lon_change < 0:
            new_latitude = location[0] + (distance_lat * m)
            new_longitude = location[1] + (distance_lon * m) / cos(location[0] * (pi / 180))
        elif lat_change >0 and lon_change > 0:
            new_latitude = location[0] - (distance_lat * m)
            new_longitude = location[1] - (distance_lon * m) / cos(location[0] * (pi / 180))
            if angle + rotation >90:
                pass
        elif lat_change <0 and lon_change > 0:
            new_latitude = location[0] + (distance_lat * m)
            new_longitude = location[1] - (distance_lon * m) / cos(location[0] * (pi / 180))
        elif lat_change >0 and lon_change < 0:
            new_latitude = location[0] - (distance_lat * m)
            new_longitude = location[1] + (distance_lon * m) / cos(location[0] * (pi / 180))
        p = p +1
        return [new_latitude,new_longitude]
    
    def _time(self):
        time_format = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        self.time_label.config(text="Sunucu Saati:{}".format(time_format),font=("Arial",16))
        #self.time_label.after(10,self._time)

    def _telemetry_label(self):
        global our_telemetry
        self.telemetry_label.config(text = our_telemetry,font=("Arial",16))
        #self.telemetry_label.after(10,self._telemetry_label)

    def __camera(self):

            _, self.frame = self.cap.read()
            if self.recording == True:
                self._out.write(self.frame)
            if self.record_stopped == True:
                self._out.release()
            cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.panel.imgtk = imgtk
            self.panel.configure(image=imgtk)
            self.panel.after(1,self.__camera)
    def record_video(self):
        self.recording = True
    def stop_recording(self):
        self.record_stopped = True
    def ReturnHome(self):
        global rtl_cmd 
        rtl_cmd = True
    def Guided(self):
        global guided_cmd
        guided_cmd = True
    def Loiter(self):
        global loiter_cmd
        loiter_cmd = True
    def _getoptions(self):
        global mode , otonom_kalkış_cmd , otonom_iniş_cmd , Manual_cmd , kamikaze_cmd , otonom_it_dalaşı_cmd , mode_1 , mode_2
        selected_option = self.options.get()
        if selected_option == "Otonom Kalkış":
            otonom_kalkış_cmd = True
            mode = mode_1
        elif selected_option == "Otonom İniş":
            otonom_iniş_cmd = True
            mode = mode_1
        elif selected_option == "Manual":
            Manual_cmd = True
            mode = mode_2
        elif selected_option == "Kamikaze":
            kamikaze_cmd = True
        elif selected_option == "Otonom İt Dalaşı":
            otonom_it_dalaşı_cmd = True
        else:
            pass
        return selected_option

    def Sunucu_Bağlan(self):
        global transmit_start 
        transmit_start = True
    def Sunucu_Çıkış(self):
        global transmit_stopped
        transmit_stopped = True 
    def Transmit_Başla(self):
        global transmit_start
        if transmit_start == True :
            timer = RepeatTimer(1,Communication)  
            timer.start() #recalling run     
    def start_mission(self):
        global mission_start
        mission_start = True
    def __init__(self):
        global uav_port
        global locking_count
        global mode
        global uav_host
        global client_socket_uav
        self.recording = False
        self.record_stopped = False
        self._fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self._out = cv2.VideoWriter("output.mp4", self._fourcc, 20.0, (640,480))
        self.geodesic = Geod(ellps='WGS84')

        client_socket_uav = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
        client_socket_uav.connect((uav_host, uav_port))  # connect to the server
        self.categorization = Categorize(1)  

        self.window_initialized = False
        self.panel = None
        self.mainWindow = tkinter.Tk()
        self.mainWindow.title("HÜMA VECİHİ SİHA PANEL")
        self.mainWindow.geometry('1500x800')
        self.mainWindow['padx'] = 8
        # Capture from camera
        #self.cap = cv2.VideoCapture(0)
        
        label= tkinter.Label(self.mainWindow, text="Vecihi HÜMA SİHA",font=("Arial",25))
        label.grid(row=0, column=0, columnspan=2)

        self.mainWindow.columnconfigure(0, weight=100)
        self.mainWindow.columnconfigure(1, weight=10)
        self.mainWindow.columnconfigure(2, weight=100)
        self.mainWindow.columnconfigure(3, weight=1000)
        self.mainWindow.columnconfigure(4, weight=1000)
        self.mainWindow.columnconfigure(5, weight=100)
        self.mainWindow.rowconfigure(0, weight=5)
        self.mainWindow.rowconfigure(1, weight=12)
        self.mainWindow.rowconfigure(2, weight=10)
        self.mainWindow.rowconfigure(3, weight=5)
        self.mainWindow.rowconfigure(4, weight=5)
        self.mainWindow.rowconfigure(5, weight=3)
        self.mainWindow.rowconfigure(6, weight=3)

        self.map_widget = tkintermapview.TkinterMapView(self.mainWindow,width=480,height=420,corner_radius=10)
        self.map_widget.set_position(39.856398, 32.780181)
        self.map_widget.set_zoom(16)
        self.create_polygon()
        self.map_widget.grid(row=1, column=0, sticky='nsew', rowspan=2)
        self.map_widget.config(border=2, relief='sunken')
        

        # Create the list of options
        options_list = ["Otonom Kalkış", "Otonom İt Dalaşı", "Kamikaze ", "Otonom İniş" ,"Manual"]
        self.options = tkinter.StringVar(master=self.mainWindow)
        self.options.set("Select an operation")
        self.operations = tkinter.OptionMenu(self.mainWindow,self.options,*options_list)
        self.operations.config(width=15,height=3,background="lightblue",border=5)
        self.operations.grid(row=2,column=4,sticky='sw')
        ####STATE VARIABLES#####
        state_1= tkinter.Label(self.mainWindow, text="Operasyon Modu :{}\nBağlantı:Aktif\nDurum Bilgisi:ID:5'ten kaçıyor\nToplam Kilitlenme Sayısı:{}".format(mode,locking_count),font=("Arial",13),background="darkgrey")
        state_1.config(width=30,height=4)
        state_1.grid(row=2,column=2)
        #########Sunucu Saati ve Telemetri Bilgileri###############
        self.time_label = tkinter.Label(self.mainWindow)
        self.time_label.config(text="Sunucu Saati:",font=("Arial",18))
        self.time_label.grid(row=0,column = 2)
        self.telemetry_label = tkinter.Label(self.mainWindow,wraplength=250)
        self.telemetry_label.grid(row = 1,column=2)
        # Frame for the time spinners
        """ timeFrame = tkinter.LabelFrame(self.mainWindow, text="Time")
        timeFrame.grid(row=3, column=0, sticky='new') """
        ##Camera
        self.panel = tkinter.Label(self.mainWindow)
        self.panel.grid(row=1,column=4)
        # Buttons
        okButton = tkinter.Button(self.mainWindow, text="OK",command=self.start_mission)
        okButton.config(width=15,height= 3,background='darkgreen',border=10)
        cancelButton = tkinter.Button(self.mainWindow, text="Cancel", command=self.mainWindow.destroy)
        cancelButton.config(width=15,height= 3,background='red',border=10)
        okButton.grid(row=5, column=4, sticky='e')
        cancelButton.grid(row=5, column=5, sticky='w')
        self.submit_button = tkinter.Button(self.mainWindow,text='Komut Yolla',command=self._getoptions)
        self.submit_button.config(width=16,height=3,background='brown',border=5)
        self.submit_button.grid(row =3 , column= 4 ,sticky='sw')
        ####Record Buttons#############
        self.record_video_button = tkinter.Button(self.mainWindow,text = "Kayıt Başlat",command=self.record_video)
        self.record_video_button.config(width=15,height=3,background="lightgreen",border = 2)
        self.record_video_button.grid(row = 4,column=4,sticky='sw')
        self.stop_recording_button = tkinter.Button(self.mainWindow,text = "Kayıt Durdur",command=self.stop_recording)
        self.stop_recording_button.config(width=15,height=3,background="red",border = 2)
        self.stop_recording_button.grid(row = 5,column=4,sticky='sw')
        #### MissionPlanner Mod Seçimleri##########
        self.rtl_button = tkinter.Button(self.mainWindow,text = "RTL",command=self.ReturnHome)
        self.rtl_button.config(width=15,height=3,background="darkgray",border = 2)
        self.rtl_button.grid(row = 3,column=0,sticky='sw')
        self.guided_button = tkinter.Button(self.mainWindow,text = "GUIDED",command=self.Guided)
        self.guided_button.config(width=15,height=3,background="darkgray",border = 2)
        self.guided_button.grid(row = 4,column=0,sticky='sw')
        self.loiter_button = tkinter.Button(self.mainWindow,text = "LOITER",command=self.Loiter)
        self.loiter_button.config(width=15,height=3,background="darkgray",border = 2)
        self.loiter_button.grid(row = 5,column=0,sticky='sw')
        ### Sunucu Bağlan ###
        self.server_connect = tkinter.Button(self.mainWindow,text = "Sunucuya Bağlan",command=self.Sunucu_Bağlan)
        self.server_connect.config(width=15,height=3,background="darkgray",border = 2)
        self.server_connect.grid(row = 3,column=2,sticky='sw')
        ### Sunucu Göndermeye Başla ###
        self.start_transmit = tkinter.Button(self.mainWindow,text = "İletişime Başla",command=self.Transmit_Başla)
        self.start_transmit.config(width=15,height=3,background="darkgray",border = 2)
        self.start_transmit.grid(row = 4,column=2,sticky='sw')
        ### Sunucu Çık ###
        self.server_exit = tkinter.Button(self.mainWindow,text = "Sunucudan ayrıl",command=self.Sunucu_Çıkış)
        self.server_exit.config(width=15,height=3,background="darkgray",border = 2)
        self.server_exit.grid(row = 5,column=2,sticky='sw')
        ### Sunucu IP giriş yeri ####
        self.ip_label = tkinter.Label(self.mainWindow,text = "IP Adresini giriniz",font=("Arial",16))
        self.ip_label.grid(row = 2,column=5,sticky='sw')
        self.ip_entry_box = tkinter.Entry(self.mainWindow,width=20)
        self.ip_entry_box.grid(row = 3,column=5,sticky='sw')
        global team_number
        self.update(team_number)
        self.update2()
        #self.map_widget.after(1, self.update,team_number)
    
    def run(self):
        #self.t = threading.Thread(target=self.__camera)
        #self.t.setDaemon(True)
        #self.t.start()    
        self.widget_thread = threading.Thread(target=self.widget_update)
        self.widget_thread.setDaemon(True)
        self.widget_thread.start()
        self.mainWindow.mainloop()
    def update(self,team_number):
        global mode
        self._time()
        state_1= tkinter.Label(self.mainWindow, text="Operasyon Modu :{}\nBağlantı:Aktif\nDurum Bilgisi:ID:5'ten kaçıyor\nToplam Kilitlenme Sayısı:{}".format(mode,locking_count),font=("Arial",13),background="darkgrey")
        state_1.config(width=30,height=4)
        state_1.grid(row=2,column=2)
        self.map_widget.after(30, self.update,team_number)
    def update2(self):
        categorized_data = self.categorization.flight_controller()
        self.map_widget.after(1000, self.update2)
    def widget_update(self):
            global start2 
            global our_telemetry
            global enemy_prev_list
            global coordinates_prev
            global window_initialized
            global in_waiting
            global enemy_list
            global prev_drawing
            global drawing_initialized
        
            if start2 == 0:
                start2 = datetime.now()
            diff2 = (datetime.now() - start2).seconds
            if diff2 == 1:
                self._telemetry_label()
                start2 = 0
                if drawing_initialized == True:
                    if self.window_initialized == False :
                        a = 0
                        for enemy in enemy_list :
                            if enemy == []:
                                a = a +1
                                enemy_prev_list.pop(a)
                            a = a +1
                        enemy_prev_list = enemy_list
                        self.window_initialized = True
                    i = 0
                    if enemy_list != 0:
                        enemy_next_list=enemy_list[1]
                        enemy = enemy_list[0]
                        enemy_prev2 = enemy_prev_list[1]
                        enemy_prev1 = enemy_prev_list[0]
                        condition = True
                        try:
                            for a in enemy:
                                if a["takim_numarasi"] == team_number:
                                    our_telemetry = a
                            for b in enemy_prev1:
                                if b["takim_numarasi"] == team_number:
                                    dummy = "OK"
                        except Exception as e :
                            condition = False

                        if condition == True:
                            if prev_drawing[0][0][0] != 0:
                                for i in range(len(enemy_list[0])):
                                    for j in range(3):
                                        self.map_widget.delete(prev_drawing[0][i][j])    
                                        self.map_widget.delete(prev_drawing[1][i][j])  
                            for a in range(len(enemy)):
                                coordinates_prev = (enemy[a]["IHA_enlem"],enemy[a]["IHA_boylam"])
                                coordinates = (enemy_next_list[a]["IHA_enlem"],enemy_next_list[a]["IHA_boylam"])
                                coordinates_prev1 = (enemy_prev1[a]["IHA_enlem"],enemy_prev1[a]["IHA_boylam"])
                                coordinates1 = (enemy_prev2[a]["IHA_enlem"],enemy_prev2[a]["IHA_boylam"])
                                rotation = 10*math.atan((coordinates[1]-coordinates_prev[1])/(coordinates[0]-(coordinates_prev[0])))
                                rotation = rotation -180
                                rotation1 = 10*math.atan((coordinates1[1]-coordinates_prev1[1])/(coordinates1[0]-(coordinates_prev1[0])))
                                rotation1 = rotation -180
                                lon_change = coordinates[1]-coordinates_prev[1]
                                lat_change = coordinates[0]-coordinates_prev[0]
                                lon_change1 = coordinates1[1]-coordinates_prev1[1]
                                lat_change1 = coordinates1[0]-coordinates_prev1[0]

                                if rotation <0:
                                    line_rotation_right = rotation+32
                                    line_rotation_left = rotation-32
                                elif rotation >0:
                                    line_rotation_right = rotation+32
                                    line_rotation_left = rotation-32
                                if rotation1 <0:
                                    line_rotation_right1 = rotation1+32
                                    line_rotation_left1 = rotation1-32
                                elif rotation1 >0:
                                    line_rotation_right1 = rotation1+32
                                    line_rotation_left1 = rotation1-32

                                rot=self.geodesic.inv(coordinates_prev[1],coordinates_prev[0],coordinates[1],coordinates[0])
                                left_line=Window._set_watch_points(distance=80,angle=line_rotation_left,location=coordinates,lat_change=lat_change,lon_change=lon_change,rotation=rotation)
                                right_line = Window._set_watch_points(distance=80,angle=line_rotation_right,location=coordinates,lat_change=lat_change,lon_change=lon_change,rotation=rotation)
                                left_line2 = Window._set_watch_points(distance=80,angle=line_rotation_left1,location=coordinates1,lat_change=lat_change1,lon_change=lon_change1,rotation=rotation1)
                                right_line2 =  Window._set_watch_points(distance=80,angle=line_rotation_right1,location=coordinates1,lat_change=lat_change1,lon_change=lon_change1,rotation=rotation1)
                                fill_color = "blue"
                                if team_number == enemy[a]["takim_numarasi"]:
                                    fill_color = "black"
                                search_edges = [left_line,right_line,coordinates]
                                search_edges1 = [left_line2,right_line2,coordinates1]
                                prev_drawing[1][a][0] =  self.map_widget.set_path(position_list=[coordinates_prev,coordinates],color=fill_color,width = 2)
                                prev_drawing[1][a][1] = self.map_widget.set_path(position_list=[coordinates,left_line],color=fill_color,width = 2)
                                prev_drawing[1][a][2] = self.map_widget.set_path(position_list=[coordinates,right_line],color=fill_color,width = 2)
                                prev_drawing[0][a][0] =  self.map_widget.set_path(position_list=[coordinates_prev1,coordinates1],color=fill_color,width = 2)
                                prev_drawing[0][a][1] = self.map_widget.set_polygon(position_list=search_edges,fill_color = "red",border_width = 3)
                                prev_drawing[0][a][2] = 0
                                
                                i = i +1
                            
                        enemy_prev_list = enemy_list
            self.map_widget.after(20, self.widget_update)

    def create_polygon(self):
        z1 = (39.857619, 32.774545)
        z2 = (39.858754, 32.783149)
        z3 = (39.851495, 32.780057)
        z4 = (39.854076, 32.787676)
        z1_3 = ((z1[0] + z3[0])/2,(z1[1] + z3[1])/2)
        z1_2 = ((z2[0] + z1[0])/2,(z2[1] + z1[1])/2)
        z2_4 = ((z2[0] + z4[0])/2,(z2[1] + z4[1])/2)
        z3_4 = ((z3[0] + z4[0])/2,(z3[1] + z4[1])/2)
        z_middle = ((z1_2[0] + z3_4[0])/2,(z1_2[1] + z3_4[1])/2)
        q1_1 = ((z1_2[0] + z2[0])/2,(z1_2[1] + z2[1])/2)
        q1_2 = ((z2[0] + z2_4[0])/2,(z2[1] + z2_4[1])/2)
        q1_3 = ((z2_4[0] + z_middle[0])/2,(z2_4[1] + z_middle[1])/2)
        q1_4 = ((z_middle[0] + z1_2[0])/2,(z_middle[1] + z1_2[1])/2)
        q1_middle = ((q1_1[0] + q1_3[0])/2,(q1_1[1] + q1_3[1])/2)
        q2_1 = ((z1[0] + z1_2[0])/2,(z1[1] + z1_2[1])/2)
        q2_3 = ((z1_3[0] + z_middle[0])/2,(z1_3[1] + z_middle[1])/2)
        q2_4 = ((z1[0] + z1_3[0])/2,(z1[1] + z1_3[1])/2)
        q2_middle = ((q2_1[0] + q2_3[0])/2,(q2_1[1] + q2_3[1])/2)
        q3_2 = ((z_middle[0] + z3_4[0])/2,(z_middle[1] + z3_4[1])/2)
        q3_3 = ((z3_4[0] + z3[0])/2,(z3_4[1] + z3[1])/2)
        q3_4 = ((z1_3[0] + z3[0])/2,(z1_3[1] + z3[1])/2)
        q3_middle = ((q2_3[0] + q3_3[0])/2,(q2_3[1] + q3_3[1])/2)
        q4_2 = ((z2_4[0] + z4[0])/2,(z2_4[1] + z4[1])/2)
        q4_3 = ((z4[0] + z3_4[0])/2,(z4[1] + z3_4[1])/2)
        q4_middle = ((q1_3[0] + q4_3[0])/2,(q1_3[1] + q4_3[1])/2)
        edges = [z1,z2,z4,z3]
        points = [z1_3,z1_2,z2_4,z3_4,z_middle]
        side_points = [q1_1,q1_2,q1_3,q1_4,q2_1,q2_3,q2_4,q3_2,q3_3,q3_4,q4_2,q4_3,q1_middle,q2_middle,q3_middle,q4_middle]
        try :
            self.map_widget.set_polygon(position_list=edges)
            self.map_widget.set_path(position_list=[z_middle,points[0]],color="red",width = 1)
            self.map_widget.set_path(position_list=[z_middle,points[1]],color="red",width = 1)
            self.map_widget.set_path(position_list=[z_middle,points[2]],color="red",width = 1)
            self.map_widget.set_path(position_list=[z_middle,points[3]],color="red",width = 1)

            self.map_widget.set_path(position_list=[q1_middle,side_points[0]],color="red",width = 1)
            self.map_widget.set_path(position_list=[q1_middle,side_points[1]],color="red",width = 1)
            self.map_widget.set_path(position_list=[q1_middle,side_points[2]],color="red",width = 1)
            self.map_widget.set_path(position_list=[q1_middle,side_points[3]],color="red",width = 1)

            self.map_widget.set_path(position_list=[q2_middle,side_points[4]],color="red",width = 1)
            self.map_widget.set_path(position_list=[q2_middle,side_points[3]],color="red",width = 1)
            self.map_widget.set_path(position_list=[q2_middle,side_points[5]],color="red",width = 1)
            self.map_widget.set_path(position_list=[q2_middle,side_points[6]],color="red",width = 1)

            self.map_widget.set_path(position_list=[q3_middle,side_points[5]],color="red",width = 1)
            self.map_widget.set_path(position_list=[q3_middle,side_points[7]],color="red",width = 1)
            self.map_widget.set_path(position_list=[q3_middle,side_points[8]],color="red",width = 1)
            self.map_widget.set_path(position_list=[q3_middle,side_points[9]],color="red",width = 1)

            self.map_widget.set_path(position_list=[q4_middle,side_points[2]],color="red",width = 1)
            self.map_widget.set_path(position_list=[q4_middle,side_points[10]],color="red",width = 1)
            self.map_widget.set_path(position_list=[q4_middle,side_points[11]],color="red",width = 1)
            self.map_widget.set_path(position_list=[q4_middle,side_points[7]],color="red",width = 1)
        
            return self.map_widget
        except Exception as e :
            print("There is a error")
            return False

enemy_list_prev = 0
def Communication():
                global start
                global host
                global port
                global enemy_list
                global enemy_list_prev
                global prev_drawing
                global drawing_initialized
                global client_socket_uav
                global tx_data
                global message_ready
                action = "get"
                value = "/api/telemetri_gonder"
                request = ServerConnection.create_request(action, value)
                ServerConnection.start_connection(host, port,action,request)
                try:
                    while True:
                        events = sel.select(timeout=0)
                        for key, mask in events:
                            message = key.data
                            try:
                                enemy_list = message.process_events(mask)
                                
                                if enemy_list == enemy_list_prev :
                                    enemy_list = 0
                                
                                """ if enemy_list != 0 :
                                    enemy_list_copy = enemy_list
                                    #enemy_list_copy = pickle.dumps(enemy_list_copy)
                                    tx_data = pickle.dumps(tx_data)
                                    enemy_list_prev = enemy_list
                                    if tx_data != 0 :
                                        client_socket_uav.send(tx_data)  # send message """
                                
                                if drawing_initialized == False and enemy_list != 0:
                                    if enemy_list == [0,0]:
                                        drawing_initialized = False
                                    else:
                                        dummy_count = 0
                                        for i in range(len(enemy_list)):
                                            prev_drawing.append([])
                                            for j in range(len(enemy_list[0])):
                                                prev_drawing[i].append([0,0,0])
                                                dummy_count += 1
                                        drawing_initialized = True
                            except Exception:
                                print(
                                    f"Main: Error: Exception for {message.addr}:\n"
                                    f"{traceback.format_exc()}"
                                )
                                message.close()
                                #self.client_socket_uav.close()  # close the connection
                        # Check for a socket being monitored to continue.
                        if not sel.get_map():
                            break
                except KeyboardInterrupt:
                    print("Caught keyboard interrupt, exiting")
                finally:
                    #self.client_socket_uav.close()  # close the connection
                    sel.close()

class RepeatTimer(Timer):  
    def run(self):  
        global transmit_stopped
        while not self.finished.wait(self.interval):  
            self.function(*self.args,**self.kwargs)  
            print(' ')  
            if transmit_stopped == True:
                break

if __name__ == "__main__":
    window= Window()
    window.run()
    
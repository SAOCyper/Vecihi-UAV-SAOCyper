import geopy.distance
import math
import sys
sys.path.insert(1, r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\src\modules')
import telemetry_data

from math import sin, cos, sqrt, atan2, radians ,acos ,degrees,atan,asin
from datetime import datetime
import numpy as np
from shapely.geometry import Polygon
import customtkinter
import threading,folium,os
import time
from selenium import webdriver
from pyproj import Geod
from PIL import ImageTk, Image
from geographiclib.geodesic import Geodesic
import matplotlib.pyplot as plt
from scipy.interpolate import *
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge
import numpy as np

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
class Decider():
    def __init__(self,team_number:int,starting_point:list):
        self.auto = AutoPilot(starting_point =starting_point)
        self.team_number = team_number
        self.count = 0
        self.corresponding_enemy_list = []
        self.enemy_list = []
        self.is_initialized = False
        self.prev_list_initialized = False
        self.on_loop = False
        self.sorted_list_counter = 0

    def flight_controller(self,incoming_data:list):
        global previous_location_list
        global k
        #setup array-list starters
        if not self.is_initialized:
            for i in incoming_data:
                #if i["takim_numarasi"] != self.team_number:
                    #self.enemy_list.append(i)
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
            self.is_initialized = True # Set True for starter setup
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
            print(enemy["takim_numarasi"])
            horizontal_difference ,bearing_angle ,alt_command,uDirection,lat_change,lon_change,self.enemy, rakip_irtifa ,diff_irtifa,Qrotate,Qtrack,turn_direction_for_enemy,turn_direction_for_us,where_is_enemy=self.auto.angle_calc(us=us,us_prev=us_prev,prev_enlem=prev_enlem,prev_boylam=prev_boylam,prev_irtifa=prev_irtifa,rakip_enlem= enemy["IHA_enlem"],rakip_boylam= enemy["IHA_boylam"],rakip_irtifa= enemy["IHA_irtifa"])
            result_listed={"enemy_id":enemy["takim_numarasi"],"Enlem":self.enemy[0],"Boylam":self.enemy[1],"İrtifa":rakip_irtifa,"İrtifa_Farkı":diff_irtifa,"bearing_angle":bearing_angle , "horizantal_distance":horizontal_difference,"lat_change":lat_change,"lot_change":lon_change,"alt_command":alt_command,"Plane_Direction":uDirection,"Qrotate":Qrotate,"Qtrack":Qtrack,"turn_direction_for_enemy":turn_direction_for_enemy,"turn_direction_for_us":turn_direction_for_us,"where_is_enemy":where_is_enemy}
            self.corresponding_enemy_list[enemy["takim_numarasi"] - 1].append(result_listed)
            global count
            count = count +1
        var=(team_count * 4) + 1
        if count >= var:
            self.polynomial_calc()
            for t in range(team_count):
                self.corresponding_enemy_list[t].pop(0)
            count = (team_count * 4)
        k = k +1   
        previous_location_list = incoming_data 
            
        #get polynomial location changes -----------------------------
        #Trim the array
        b = 0
        check_flag = []
        for i in self.corresponding_enemy_list:
            if b !=0 and i == check_flag:
                del self.corresponding_enemy_list[b:]
                break
            b = b+1
        self.create_command()
        return [self.corresponding_enemy_list]
        
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
        #print(y_pred_lat,y_pred_lon,pred_time)
        return y_pred_lat,y_pred_lon,pred_time

    def polynomial_calc(self):
        polynomial_list = []
        time = [1,2,3,4,5]
        enlem_list = []
        boylam_list = []
        irtifa_list = []
        for enemy in self.corresponding_enemy_list:
            enlem_list.clear()
            boylam_list.clear()
            irtifa_list.clear()
            res = 0.5 # interpolation resolution (in meters)
            deg = 2 # interpolation degree N (N = 1 for linear interpolation, 2 <= N <= 5 for spline interpolation)
            for plane in enemy:
                
                enlem_list.append(plane["Enlem"])
                boylam_list.append(plane["Boylam"])
                irtifa_list.append(plane["İrtifa"])
            lat , lon , ele = self.GPX_interpolate(enlem_list,boylam_list,irtifa_list,res=res,deg = deg)
            for i in range(len(enlem_list)):
                polynomial_list.append([enlem_list[i],boylam_list[i]])

            pred_lat,pred_lon,pred_time=self.polynomial_pred(lat,lon,ele,6)
            enlem_list.append(pred_lat)
            boylam_list.append(pred_lon)
            time.append(pred_time)
            """ ax = plt.axes(projection='3d')
            plt.rcParams["figure.autolayout"] = True
            ax.scatter(enlem_list, boylam_list, time)
            ax.set_xlabel('Latitude', labelpad=20)
            ax.set_ylabel('Longitude', labelpad=20)
            ax.set_zlabel('Altitude', labelpad=20)
            ax.plot(enlem_list, boylam_list, time, color="black")
            time.pop(-1)
            plt.xlabel("latitude")
            plt.ylabel("longitude")
            plt.show()
            plt.close('all')  """

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
            data = [lat, lon, ele]
            tck, _ = splprep(x = data, u = dist_cum_norm, k = int(deg), s = 0, nest = len(lat)+deg+1)
            u_interp = np.linspace(0, 1, 50)
            out = splev(u_interp, tck)
            lat_interp = out[0]
            lon_interp = out[1]
            ele_interp = out[2]
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

    def create_command(self):
        characteristics_list = self.get_characteristics()
        in_range_count = 0
        in_range_list = [0,0,0]
        base_angle = 0
        for enemy in self.corresponding_enemy_list:
            if enemy[-1]["enemy_id"] == self.team_number:
                base_angle = enemy[-1]["bearing_angle"]
            if enemy != []:
                if enemy[-1]["alt_command"] == "Dive":
                    alt_command = "Rise"
                elif enemy[-1]["alt_command"] == "Rise":
                    alt_command = "Dive"
                

                if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("priority1") == True and characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("is_dangerous")== True:
                    speed = 75
                    if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("avoid_immediate") == True:
                        speed = 100
                    escape_angle= 90 + enemy[-1]["Qrotate"]
                    in_range_list[0]=[enemy[-1]["turn_direction_for_us"],escape_angle,alt_command,speed]
                    in_range_count = in_range_count + 1
                elif characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("priority2") == True and characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("is_dangerous")== True:
                    speed = 75 
                    if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("avoid_immediate") == True:
                        speed = 100
                    escape_angle= 90 + enemy[-1]["Qrotate"]
                    in_range_count = in_range_count + 1
                    in_range_list[1]=[enemy[-1]["turn_direction_for_enemy"],escape_angle,alt_command,speed]
                elif characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("priority3") == True and characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("is_dangerous")== True:
                    speed = 75
                    if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("avoid_immediate") == True:
                        speed = 100
                    escape_angle= 90 + enemy[-1]["Qrotate"]
                    in_range_count = in_range_count + 1
                    in_range_list[2]=[enemy[-1]["turn_direction_for_enemy"],escape_angle,alt_command,speed]
                else : 
                    continue
        if in_range_count == 1:
            for i in in_range_list:
                if i != 0:
                    #turn_angle = abs(i[1] - i[2] )
                    print("Turn {} with {} , {} and accelerate at %{} speed \n".format(i[0],i[1],i[3],i[4]))
        elif in_range_count == 2:
            print("Slow down to the %10 speed and turn right")
        elif in_range_count == 3:
            print("Slow down to the %10 speed and turn right and dive")
        self.enemy_list.clear()
        return True
                                  
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
                    #self.corresponding_enemy_list.remove(enemy)
                    prev_distance_list = prev_distance_list |  {"enemy_id{}".format(enemy[0]["enemy_id"]):enemy[0]["horizantal_distance"]}
            self.prev_list_initialized = True
        for enemy in self.corresponding_enemy_list:  
            horizantal_angle_change = 0
            total_angle_change = 0
            horizantal_distance_change = 0 
            
            if enemy != []:
                
                if enemy[-1] != 0:
                    horizantal_angle_change = enemy[-1]["bearing_angle"] - horizantal_angle_change
                    """ total_angle_change = enemy[-1]["total_angle"] - total_angle_change """
                    horizantal_distance_change = enemy[-1]["horizantal_distance"] - prev_distance_list["enemy_id{}".format(enemy[-1]["enemy_id"])]
                    prev_distance_list["enemy_id{}".format(enemy[-1]["enemy_id"])] = enemy[-1]["horizantal_distance"]
                    line_rotation_right = enemy[-1]["bearing_angle"]+32
                    line_rotation_left = enemy[-1]["bearing_angle"]-32
                    right_line=self.new_location_set(distance=80,angle=line_rotation_right,location=[enemy[-1]["Enlem"],enemy[-1]["Boylam"]],lat_change=enemy[-1]["lat_change"],lon_change=enemy[-1]["lot_change"],rotation=enemy[-1]["bearing_angle"])
                    left_line=self.new_location_set(distance=80,angle=line_rotation_left,location=[enemy[-1]["Enlem"],enemy[-1]["Boylam"]],lat_change=enemy[-1]["lat_change"],lon_change=enemy[-1]["lot_change"],rotation=enemy[-1]["bearing_angle"])
                
                if horizantal_distance_change >0:
                        is_approaching = False
                        is_watching = False
                        is_in_watch_list = False
                        is_dangerous = False
                        avoid_immediate = False
                elif horizantal_distance_change < 0:
                        is_approaching = True
                        if enemy[-1]["where_is_enemy"] == "behind":
                            if enemy[-1]["Qrotate"] <45 and enemy[-1]["Qrotate"] >-45:
                                if enemy[-1]["horizantal_distance"] < 80:    
                                    is_dangerous = True
                                    is_watching = True
                                    is_in_watch_list = True
                                    avoid_immediate = False
                                elif enemy[-1]["horizantal_distance"] < 50:
                                    is_dangerous = True
                                    is_watching = True
                                    is_in_watch_list = True
                                    avoid_immediate = True
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
        print(behaviour_dict)
        return behaviour_dict
     
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
            if enemy != []:
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



class AutoPilot():
    """Calculates necessary angles , directions , x and y coordinates , 
       altitude differences between 1 plane with other planes in a given set 
       which consists of telemetry datas.
    """
    def __init__(self,starting_point:list):
        self.R = 6373.0
        self.p0 = {"lat":39.860153,"lng":32.773298}
        self.p1=  {"lat":39.844360,"lng":32.793870}
        self.z1 = (39.860948, 32.770010)
        self.z2 = (39.864205,32.788550)
        self.z3 = (39.844797, 32.781285)
        self.z4 = (39.853096, 32.806683)
        self.generate_map(self.p0,self.p1)
        self.generate_poly(self.z1,self.z2,self.z3,self.z4)
        self.start_x ,self.start_y = self.get_x_y_coordinates(starting_point[0],starting_point[1])
        self.start_x = self.map_mid_x - self.start_x
        self.start_y = (self.map_mid_y - self.start_y) * -1
        self.estimation_initialized = False
    def generate_poly(self,p1,p2,p3,p4):
        self.poly = Polygon((p1,p2,p3,p4))
        #print(self.poly)
    def generate_map(self,p0:dict,p1:dict):
        """Generates a small map for minimalizing the errors for calculating
            angle operations 

        Args:
            p0 (dict): starting point of generated map
            p1 (dict): ending point of generated map
        Returns:
            bool: True for success
        """
        self.map_start_x,self.map_start_y = self.get_x_y_coordinates(p0["lat"],p0["lng"])
        self.map_end_x,self.map_end_y = self.get_x_y_coordinates(p1["lat"],p1["lng"])
        self.map_mid_x,self.map_mid_y = (self.map_end_x + self.map_start_x)/2 ,(self.map_end_y + self.map_start_y)/2 
        return True
    def get_x_y_coordinates(self,lat:float,lng:float):
        """Returns x and y coordinates for given latitude and longitude

        Args:
            lat (float): latitude
            lng (float): longitude

        Returns:
            float: converted x and y coordinates.
        """
        x = self.R * lng * cos((self.p0["lat"] + self.p1["lat"])/2)
        x = x * -1
        y = self.R * lat
        return x ,y
    def get_direction_vector(self,x_coordinates:float,y_coordinates:float):
        delta_x=self.start_x - x_coordinates
        delta_y=self.start_y - y_coordinates
        if delta_x < 0 and delta_y < 0 :
            our_direction = "Q1"
        elif delta_x >0 and delta_y < 0 :
            our_direction = "Q2"
        elif delta_x > 0 and delta_y > 0:
            our_direction = "Q3"
        elif delta_x <0 and delta_y >0:
            our_direction = "Q4"
        plane_angle = math.degrees(atan(abs(delta_y)/abs(delta_x)))
        return  plane_angle , our_direction

    def get_bearing_angle(self,location:list,location_prev:list):

        delta_longitude = (location_prev[1]-location[1])
        y = sin(delta_longitude) * cos(location[0])
        x = (cos(location_prev[0]) * sin(location[0])) - (sin(location_prev[0]) * cos(location[0]) * cos(delta_longitude))
        bearing = atan2(y,x)
        bearing=math.degrees(bearing)
        bearing = (bearing +360) % 360
        return bearing

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
        enemy_x , enemy_y = self.get_x_y_coordinates(rakip_enlem,rakip_boylam)
        horizontal_difference=geopy.distance.geodesic(self.enemy, self.us).meters
        horizontal_difference_prev=geopy.distance.geodesic(self.prev_enemy, self.us_prev).meters
        distance_change = horizontal_difference_prev - horizontal_difference
        if self.estimation_initialized == False:
            
            self.estimation_initialized = True
        bearing_angle = self.get_bearing_angle(self.enemy,self.prev_enemy)
        our_bearing_angle = self.get_bearing_angle(self.us,self.us_prev)
        print(bearing_angle)
        Qrotate= bearing_angle - our_bearing_angle
        Qtrack = our_bearing_angle - bearing_angle
        uDirection = None
        ourDirection = None
        turn_direction_for_enemy = None
        turn_direction_for_us = None
        where_is_enemy = None
        diff_irtifa = rakip_irtifa - us[2]
        alt_command = None
        if bearing_angle <90 and bearing_angle >0:
            uDirection = "Q1"
        if bearing_angle <180 and bearing_angle >90:
            uDirection = "Q4"
        if bearing_angle <270 and bearing_angle >180:
            uDirection = "Q3"
        if bearing_angle <360 and bearing_angle >270:
            uDirection = "Q2"
        if our_bearing_angle <90 and our_bearing_angle >0:
            ourDirection = "Q1"
        if our_bearing_angle <180 and our_bearing_angle >90:
            ourDirection = "Q4"
        if our_bearing_angle <270 and our_bearing_angle >180:
            ourDirection = "Q3"
        if our_bearing_angle <360 and our_bearing_angle >270:
            ourDirection = "Q2"
        if ourDirection == "Q1" and uDirection == "Q1":
            if(self.us[0]  > self.enemy[0] and self.us[1]>self.enemy[1]):
                where_is_enemy = "behind"
            elif(self.us[0] == self.enemy[0] and self.us[1] == self.enemy[1]):
                where_is_enemy = None
            else:
                where_is_enemy = "front"
        if ourDirection == "Q1" and uDirection == "Q4":
            if(self.us[0]  < self.enemy[0] and self.us[1] > self.enemy[1]):
                where_is_enemy = "behind"
            elif(self.us[0] == self.enemy[0] and self.us[1] == self.enemy[1]):
                where_is_enemy = None
            else:
                where_is_enemy = "front"
        if ourDirection == "Q1" and uDirection == "Q2":
            if(self.us[0]  > self.enemy[0] and self.us[1]  < self.enemy[1]):
                where_is_enemy = "behind"
            elif(self.us[0] == self.enemy[0] and self.us[1] == self.enemy[1]):
                where_is_enemy = None
            else:
                where_is_enemy = "front"
        if ourDirection == "Q2" and uDirection == "Q2":
            if(self.us[0]  > self.enemy[0] and self.us[1] < self.enemy[1]):
                where_is_enemy = "behind"
            elif(self.us[0] == self.enemy[0] and self.us[1] == self.enemy[1]):
                where_is_enemy = None
            else:
                where_is_enemy = "front"
        if ourDirection == "Q2" and uDirection == "Q1":
            if(self.us[0]  > self.enemy[0] and self.us[1] > self.enemy[1]):
                where_is_enemy = "behind"
            elif(self.us[0] == self.enemy[0] and self.us[1] == self.enemy[1]):
                where_is_enemy = None
            else:
                where_is_enemy = "front"
        if ourDirection == "Q2" and uDirection == "Q3":
            if(self.us[0]  < self.enemy[0] and self.us[1] < self.enemy[1]):
                where_is_enemy = "behind"
            elif(self.us[0] == self.enemy[0] and self.us[1] == self.enemy[1]):
                where_is_enemy = None
            else:
                where_is_enemy = "front"
        if ourDirection == "Q3" and uDirection == "Q3":
            if(self.us[0]  < self.enemy[0] and self.us[1] < self.enemy[1]):
                where_is_enemy = "behind"
            elif(self.us[0] == self.enemy[0] and self.us[1] == self.enemy[1]):
                where_is_enemy = None
            else:
                where_is_enemy = "front"
        if ourDirection == "Q3" and uDirection == "Q2":
            if(self.us[0]  > self.enemy[0] and self.us[1] > self.enemy[1]):
                where_is_enemy = "behind"
            elif(self.us[0] == self.enemy[0] and self.us[1] == self.enemy[1]):
                where_is_enemy = None
            else:
                where_is_enemy = "front"
        if ourDirection == "Q3" and uDirection == "Q4":
            if(self.us[0]  < self.enemy[0] and self.us[1] < self.enemy[1]):
                where_is_enemy = "behind"
            elif(self.us[0] == self.enemy[0] and self.us[1] == self.enemy[1]):
                where_is_enemy = None
            else:
                where_is_enemy = "front"
        if ourDirection == "Q4" and uDirection == "Q4":
            if(self.us[0]  < self.enemy[0] and self.us[1] > self.enemy[1]):
                where_is_enemy = "behind"
            elif(self.us[0] == self.enemy[0] and self.us[1] == self.enemy[1]):
                where_is_enemy = None
            else:
                where_is_enemy = "front"
        if ourDirection == "Q4" and uDirection == "Q1":
            if(self.us[0]  > self.enemy[0] and self.us[1] > self.enemy[1]):
                where_is_enemy = "behind"
            elif(self.us[0] == self.enemy[0] and self.us[1] == self.enemy[1]):
                where_is_enemy = None
            else:
                where_is_enemy = "front"
        if ourDirection == "Q4" and uDirection == "Q3":
            if(self.us[0]  < self.enemy[0] and self.us[1] < self.enemy[1]):
                where_is_enemy = "behind"
            elif(self.us[0] == self.enemy[0] and self.us[1] == self.enemy[1]):
                where_is_enemy = None
            else:
                where_is_enemy = "front"
        if diff_irtifa >0:
            alt_command = "Rise"
        else:
            alt_command = "Dive"
        if Qrotate > 180 and where_is_enemy == "behind":
            Qrotate = Qrotate - 180
            turn_direction_for_enemy = "Right"
        elif (0<Qrotate and Qrotate< 180) and where_is_enemy == "behind":
            turn_direction_for_enemy = "Left"
        elif Qrotate<0 and where_is_enemy == "behind":
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
        error_rate_x ,error_rate_y= 10 , 10
        #prev_coordinates_enemylat_lon = [self.enemy,self.us]
        #Difference in total angle 
        #angle = ((enemy_x * us_x)+(enemy_y*us_y)+(rakip_irtifa*irtifa))/(sqrt((enemy_x ** 2)+(enemy_y ** 2)+(rakip_irtifa **2)) * sqrt((us_x ** 2)+(us_y ** 2)+(irtifa ** 2)))
        #angle_diff=math.degrees(acos(angle))
        return  horizontal_difference ,bearing_angle ,alt_command,uDirection , lat_change ,lon_change ,self.enemy , rakip_irtifa ,diff_irtifa,Qrotate,Qtrack,turn_direction_for_enemy,turn_direction_for_us,where_is_enemy

class Map():
    def __init__(self,enemy_list,enemy_next_list,team_number):
        self.initialized = False
        self.team_number = team_number
        global enemy_prev_list
        global coordinates_prev
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
        line_color='red'
        fill_color='orange'
        weight=2
        text='text'
        self.our_map = folium.Map(location=[39.856398, 32.780181],zoom_start=16)
        self.our_map.add_child(folium.Polygon(locations=edges, color=line_color, fill_color=fill_color,fill_opacity = 0.5,
                                                weight=weight, popup=(folium.Popup(text))))
        for i in range(len(points)):
            folium.CircleMarker(location=points[i],
                                radius=2,
                                weight=5).add_to(self.our_map)
        for i in range(len(side_points)):
            folium.CircleMarker(location=side_points[i],
                                radius=2,
                                weight=5).add_to(self.our_map)    
        folium.PolyLine(locations=[z_middle,points[0]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[z_middle,points[1]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[z_middle,points[2]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[z_middle,points[3]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        
        folium.PolyLine(locations=[q1_middle,side_points[0]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[q1_middle,side_points[1]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[q1_middle,side_points[2]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[q1_middle,side_points[3]], color="red", weight=2.5, opacity=1).add_to(self.our_map)

        folium.PolyLine(locations=[q2_middle,side_points[4]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[q2_middle,side_points[3]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[q2_middle,side_points[5]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[q2_middle,side_points[6]], color="red", weight=2.5, opacity=1).add_to(self.our_map)

        folium.PolyLine(locations=[q3_middle,side_points[5]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[q3_middle,side_points[7]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[q3_middle,side_points[8]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[q3_middle,side_points[9]], color="red", weight=2.5, opacity=1).add_to(self.our_map)

        folium.PolyLine(locations=[q4_middle,side_points[2]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[q4_middle,side_points[10]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[q4_middle,side_points[11]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        folium.PolyLine(locations=[q4_middle,side_points[7]], color="red", weight=2.5, opacity=1).add_to(self.our_map)
        
        geodesic = Geod(ellps='WGS84')
        #print(enemy_list)
        if self.initialized == False :
            a = 0
            for enemy in enemy_list :
                if enemy == []:
                    a = a +1
                    enemy_prev_list.pop(a)
                a = a +1
            enemy_prev_list = enemy_list
            self.initialized = True
        i = 0
        enemy_next_list=enemy_next_list[0]
        enemy = enemy_list[0]
        for a in range(len(enemy)):
            coordinates_prev = (enemy[i]["IHA_enlem"],enemy[i]["IHA_boylam"])
            coordinates = (enemy_next_list[i]["IHA_enlem"],enemy_next_list[i]["IHA_boylam"])
            rotation = 10*math.atan((coordinates[1]-coordinates_prev[1])/(coordinates[0]-(coordinates_prev[0])))
            rotation = rotation -180
            lon_change = coordinates[1]-coordinates_prev[1]
            lat_change = coordinates[0]-coordinates_prev[0]
            print("****************************************")
            print(enemy[i]["takim_numarasi"])
            print(rotation)
            if rotation <0:
                line_rotation_right = rotation+32
                line_rotation_left = rotation-32
            elif rotation >0:
                line_rotation_right = rotation+32
                line_rotation_left = rotation-32
            print(line_rotation_left)
            print(line_rotation_right)
            print("****************************************")
            rot=geodesic.inv(coordinates_prev[1],coordinates_prev[0],coordinates[1],coordinates[0])
            left_line=self.new_location_set(distance=100,angle=line_rotation_left,location=coordinates,lat_change=lat_change,lon_change=lon_change,rotation=rotation)
            right_line = self.new_location_set(distance=100,angle=line_rotation_right,location=coordinates,lat_change=lat_change,lon_change=lon_change,rotation=rotation)
            fill_color = "red"
            if self.team_number == enemy[i]["takim_numarasi"]:
                fill_color = "blue"
            search_edges = [left_line,right_line,coordinates]
            folium.CircleMarker(location=coordinates,
                                    radius=2,
                                    weight=5).add_to(self.our_map)
            folium.CircleMarker(location=coordinates_prev,
                                    radius=2,
                                    weight=5).add_to(self.our_map) 
            folium.PolyLine(locations=[coordinates_prev,coordinates], color="black", weight=2.5, opacity=1).add_to(self.our_map)  
            folium.PolyLine(locations=[coordinates,left_line], color="black", weight=2.5, opacity=1).add_to(self.our_map)
            folium.PolyLine(locations=[coordinates,right_line], color="black", weight=2.5, opacity=1).add_to(self.our_map)
            folium.PolyLine(locations=[coordinates,right_line], color="black", weight=2.5, opacity=1).add_to(self.our_map)
            folium.Polygon(locations=search_edges, color=line_color, fill_color="blue",fill_opacity = 0.5,
                                                weight=weight, popup=(folium.Popup("DangerZone"))).add_to(self.our_map)
            folium.RegularPolygonMarker(location=coordinates, fill_color=fill_color, number_of_sides=3, radius=10, rotation=rotation,popup="enemy_id:{}".format(enemy[i]["takim_numarasi"])).add_to(self.our_map)             
            
            i = i +1
            
        enemy_prev_list = enemy_list
        map_name = "output.html"
        self.our_map.save("output.html")
        map_url = 'file://{}/{}'.format(os.getcwd(),map_name)
        driver = webdriver.Chrome(executable_path=r"C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\src\chromedriver.exe")
        driver.get(map_url)
        time.sleep(1)
        driver.save_screenshot('output.png')
        driver.quit

    def dist(self,lat1, long1, lat2, long2):

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
    
    def new_location_set(self,distance,angle,location:list,lat_change,lon_change,rotation):
        EARTH_RADIUS_IN_METER = 6378160
        EARTH_RADIUS_IN_KM = 6378.137
        global p
        
        distance_lat = distance * cos(72)
        distance_lon = distance * sin(72)
        if p == 1:
            distance_lat = distance * cos(18)
            distance_lon = distance * sin(18)
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

def window():
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")
    root = customtkinter.CTk()
    root.geometry("1080x600")
    image1 = Image.open(r"C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\output.png")
    image1 = image1.resize((700, 550), Image.Resampling.LANCZOS)
    test = ImageTk.PhotoImage(image1)
    frame = customtkinter.CTkFrame(master = root)
    frame.pack(pady=20,padx=60,fill="both",expand=True)
    label = customtkinter.CTkLabel(master=frame,text="2D Space",text_font=("Roboto",24))
    label.pack(pady=12,padx=10)
    label1 = customtkinter.CTkLabel(master=frame,image=test)
    label1.pack(pady=12,padx=10)
    root.mainloop()

        

telemetry_list = telemetry_data.get_data()
start = datetime.now()
startpoint = [39.854818,32.781299,100]
our_location = [[39.855008,32.781415,100],[39.85512328601099, 32.78198362544963,100],[39.85517270305381, 32.78279901694268,100],[39.85471971216288, 32.78420449438465,100]]
team_number=1
drive = Decider(team_number=team_number,starting_point=startpoint)
#thread1 = threading.Thread(target=window,args=())
#thread1.start()
for i in range(7):
    behaivour_dict=drive.flight_controller(incoming_data=telemetry_list[i])
    
    time.sleep(0.987)
    #thread = threading.Thread(target=Map,args=([telemetry_list[i]],[telemetry_list[i+1]],team_number))
    #thread.start()

print(datetime.now() - start)
    
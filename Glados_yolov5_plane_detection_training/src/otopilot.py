import geopy.distance
import math
from math import sin, cos, sqrt, atan2, radians ,acos ,degrees
from datetime import datetime
import numpy as np

class Decider():
    def __init__(self,team_number:int):
        self.auto = AutoPilot()
        self.team_number = team_number
        self.count = 0
        self.corresponding_enemy_list = []
        self.result_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.enemy_list = []
        self.is_initialized = False
    def set_enemy_list(self,incoming_data:list,our_location:list):
        our_lat = our_location[0]
        our_lng = our_location[1]
        our_alt = our_location[2] 
        #setup array-list starters
        if not self.is_initialized:
            for i in incoming_data:
                if i["takim_numarasi"] != self.team_number:
                    self.enemy_list.append(i)
            for a in range(len(self.enemy_list)):
                self.corresponding_enemy_list.append([])
        self.is_initialized = True # Set True for starter setup
        for enemy in self.enemy_list:
            enemy_lat=enemy["IHA_enlem"]   
            enemy_lng=enemy["IHA_boylam"]  
            enemy_alt=enemy["IHA_irtifa"]  
            enemy_id = enemy["takim_numarasi"]
            horizantal_angle ,total_angle , horizantal_distance  = self.auto.angle_calc(our_lat,our_lng,our_alt,enemy_lat,enemy_lng,enemy_alt)
            result_listed={"enemy_id":enemy_id,"horizantal_angle":horizantal_angle ,"total_angle":total_angle , "horizantal_distance":horizantal_distance }
            self.corresponding_enemy_list[enemy_id - 1].append(result_listed)
            self.count = self.count +1
            if self.count >= 21:
                self.corresponding_enemy_list[enemy_id - 1].pop(0)
                fake_array = 0
                self.corresponding_enemy_list[enemy_id - 1].append(fake_array)
                self.count = 20
        #Trim the array
        b = 0
        check_flag = []
        for i in self.corresponding_enemy_list:
            if b !=0 and i == check_flag:
                del self.corresponding_enemy_list[b:]
                break
                #self.corresponding_enemy_list.pop(b)
            b = b+1
        print(self.corresponding_enemy_list)
        self.predict_plane_roads()

    def predict_plane_roads(self) ->dict:
        """From all gps inputs it is checking all planes for 
        if they are closing on us or not and returning an boolean dictionary

        is_approaching : True means a plane is closing the distance between us
        is_watching : True means this plane is entered for watchzone area
        is_in_watchlist : True means this plane is in now possible threats
        is_dangerous : True means there is a follower on us bail out
        Returns:
            dict: Boolean Dictionary filled with condition flags
        """
        behaviour_dict = {}
        c = 0
        is_approaching = False
        is_watching = False
        is_in_watch_list = False
        is_dangerous = False
        avoid_immediate = False
        for enemy in self.corresponding_enemy_list:
            horizantal_angle_change = 0
            total_angle_change = 0
            horizantal_distance_change = 0 
            if enemy != []:
                for i in range(len(enemy)):
                    if enemy[i] != 0:
                        horizantal_angle_change = enemy[i]["horizantal_angle"] - horizantal_angle_change
                        total_angle_change = enemy[i]["total_angle"] - total_angle_change
                        horizantal_distance_change = enemy[i]["horizantal_distance"] - horizantal_distance_change
                if enemy[0]["horizantal_angle"] < 150:
                    if horizantal_distance_change >0:
                        is_approaching = False
                        is_watching = False
                        is_in_watch_list = False
                        is_dangerous = False
                        avoid_immediate = False
                    elif horizantal_distance_change < 0:
                        is_approaching = True
                        if horizantal_angle_change > 15 or horizantal_angle_change < -15:
                            is_in_watch_list = False
                            is_watching = True
                            is_dangerous = False
                            avoid_immediate = False
                        elif 25> horizantal_angle_change > 15 or -15 > horizantal_angle_change > -25 : 
                            is_in_watch_list = True
                            is_watching = True
                            is_dangerous = False
                            avoid_immediate = False
                        elif 15> horizantal_angle_change > 5 or -5 > horizantal_angle_change > -15 :
                            if enemy[0]["horizantal_distance"] < 30:
                                is_dangerous = True
                                is_watching = True
                                is_in_watch_list = True
                                avoid_immediate = False
                            else:
                                is_watching = True
                                is_in_watch_list = True
                                is_dangerous = False
                        elif 5 > horizantal_angle_change > -5:
                            if enemy[0]["horizantal_distance"] < 30:
                                avoid_immediate = True
                                is_watching = True
                                is_in_watch_list = True
                                is_dangerous = True
                            else:
                                avoid_immediate = False
                                is_watching = True
                                is_in_watch_list = True
                                is_dangerous = True
                    temp_dict = {"is_approaching":is_approaching,"is_watching":is_watching,"is_in_watch_list":is_in_watch_list,"is_dangerous":is_dangerous,"avoid_immediate":avoid_immediate}
                    behaviour_dict["enemy_id{}".format(enemy[0]["enemy_id"])] = temp_dict
            c = c+1
        print("**********************************")
        print("**********************************")
        print("**********************************")
        print(behaviour_dict)
        
        return behaviour_dict








class AutoPilot():
    
    def __init__(self):

        self.R = 6373.0
        self.p0 = {"lat":43.54,"lng":22.35}
        self.p1=  {"lat":43.60,"lng":22.40}
        self.generate_map(self.p0,self.p1)

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
        y = self.R * lat
        return x ,y

    def send_commands(self):
        self.angle_calc()

    def angle_calc_different_method(self,enlem:float,boylam:float,irtifa:float,rakip_enlem:float,rakip_boylam:float,rakip_irtifa:int):
        lat1 = rakip_enlem
        lon1= rakip_boylam
        lat2 = enlem
        lon2= boylam
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = self.R * c
        print(distance)
    def angle_calc(self,enlem:float,boylam:float,irtifa:float,rakip_enlem:float,rakip_boylam:float,rakip_irtifa:int):
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
        self.enemy = (rakip_enlem,rakip_boylam)
        self.us = (enlem,boylam)
        enemy_x , enemy_y = self.get_x_y_coordinates(rakip_enlem,rakip_boylam)
        us_x , us_y = self.get_x_y_coordinates(enlem,boylam)
        enemy_x = enemy_x - self.map_start_x
        enemy_y = enemy_y - self.map_start_y
        us_x = us_x - self.map_start_x
        us_y = us_y - self.map_start_y
        horizantal_angle = 0
        #Difference angle in horizantal 
        diff_x = enemy_x - us_x
        diff_y = enemy_y - us_y
        if (diff_x > 0 and diff_y > 0) or (diff_x > 0 and diff_y < 0):
            horizantal_angle = math.degrees(acos(diff_x/(sqrt((diff_x ** 2)+(diff_y ** 2)))))
            if diff_x > 0 and diff_y > 0 :
                print("Turn Left")
            else:
                print("Turn Right")
        elif (diff_x < 0 and diff_y < 0) or (diff_x < 0 and diff_y > 0):
            horizantal_angle = math.degrees(acos(diff_y/(sqrt((diff_x ** 2)+(diff_y ** 2)))))
            if diff_x < 0 and diff_y < 0 : 
                print("Turn Right")
            else:
                print("Turn Left")
        diff_irtifa = rakip_irtifa - irtifa
        if diff_irtifa >0:
            print("Rise")
        else:
            print("Dive")
        horizontal_difference=geopy.distance.geodesic(self.enemy, self.us).meters

        #Difference in total angle 
        angle = ((enemy_x * us_x)+(enemy_y*us_y)+(rakip_irtifa*irtifa))/(sqrt((enemy_x ** 2)+(enemy_y ** 2)+(rakip_irtifa **2)) * sqrt((us_x ** 2)+(us_y ** 2)+(irtifa ** 2)))
        angle_diff=math.degrees(acos(angle))
        return angle_diff , horizantal_angle , horizontal_difference



telemetry_data=[{
                            "takim_numarasi": 1,
                            "IHA_enlem": 43.576546,
                            "IHA_boylam": 22.385421,
                            "IHA_irtifa": 100,
                            "IHA_dikilme": 5,
                            "IHA_yonelme": 256,
                            "IHA_yatis": 0,
                            "IHA_hiz": 223,
                            "IHA_batarya": 20,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 315,
                            "Hedef_merkez_Y": 220,
                            "Hedef_genislik": 12,
                            "Hedef_yukseklik": 46,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 1,
                            "saniye": 23,
                            "milisaniye": 507
                            }
                            },
                            {
                            "takim_numarasi": 2,
                            "IHA_enlem": 43.584352,
                            "IHA_boylam": 22.36245421,
                            "IHA_irtifa": 90,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 2,
                            "IHA_enlem": 43.584252,
                            "IHA_boylam": 22.36245421,
                            "IHA_irtifa": 90,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },
                            {
                            "takim_numarasi": 3,
                            "IHA_enlem": 43.564352,
                            "IHA_boylam": 22.36925421,
                            "IHA_irtifa": 185,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 4,
                            "IHA_enlem": 43.578352,
                            "IHA_boylam": 22.35245421,
                            "IHA_irtifa": 115,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.614352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.615352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.616352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.620352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.621352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.622352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.624352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.628352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.630352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.631352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.633352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.635352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.640352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.645352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.648352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.652352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.65514352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.657352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            },{
                            "takim_numarasi": 5,
                            "IHA_enlem": 43.659352,
                            "IHA_boylam": 22.34245421,
                            "IHA_irtifa": 120,
                            "IHA_dikilme": 6,
                            "IHA_yonelme": 252,
                            "IHA_yatis": 2,
                            "IHA_hiz": 245,
                            "IHA_batarya": 19,
                            "IHA_otonom": 1,
                            "IHA_kilitlenme": 1,
                            "Hedef_merkez_X": 421,
                            "Hedef_merkez_Y": 240,
                            "Hedef_genislik": 143,
                            "Hedef_yukseklik": 57,
                            "GPSSaati": {
                            "saat": 19,
                            "dakika": 2,
                            "saniye": 35,
                            "milisaniye": 234
                            }
                            }]
""" auto=AutoPilot() """
start = datetime.now()
""" auto.angle_calc(43.576546,22.385421,100,43.594352,22.37245421,145) """
drive = Decider(team_number=1)
our_location = [43.584052,22.36245421,100]
drive.set_enemy_list(incoming_data=telemetry_data,our_location=our_location)
print(datetime.now() - start)
    
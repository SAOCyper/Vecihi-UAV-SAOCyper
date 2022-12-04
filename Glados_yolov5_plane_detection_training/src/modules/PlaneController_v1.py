import geopy.distance
import math,threading
from math import sin, cos, sqrt, atan2, radians ,acos ,degrees,atan
from datetime import datetime
import numpy as np
from shapely.geometry import Polygon
import tkinter
import customtkinter
prev_distance_list = {}
counter = 0
prev_coordinates = []
def Window():
    
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")
    root = customtkinter.CTk()
    root.geometry("1080x600")
    def login():
        print("Hello")
    customtkinter.DrawEngine
    frame = customtkinter.CTkFrame(master = root)
    frame.pack(pady=20,padx=60,fill="both",expand=True)
    label = customtkinter.CTkLabel(master = frame , text="2D Space",text_font=("Roboto",24))
    label.pack(pady=12,padx=10)
    root.mainloop()


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
    def flight_controller(self,incoming_data:list,our_location:list):
        our_lat = our_location[0]
        our_lng = our_location[1]
        our_alt = our_location[2] 
        #setup array-list starters
        if not self.is_initialized:
            for i in incoming_data:
                if i["takim_numarasi"] != self.team_number:
                    self.enemy_list.append(i)
            if self.on_loop == False :
                for a in range(len(self.enemy_list)+1):
                    self.corresponding_enemy_list.append([])
                self.on_loop = True
        self.is_initialized = True # Set True for starter setup
        for enemy in self.enemy_list:
            horizantal_angle , horizantal_distance ,turn_direction,alt_command,Qbetween,direction_x,direction_y  = self.auto.angle_calc(our_lat,our_lng,our_alt,enemy["IHA_enlem"],enemy["IHA_boylam"],enemy["IHA_irtifa"])
            

            result_listed={"enemy_id":enemy["takim_numarasi"],"horizantal_angle":horizantal_angle , "horizantal_distance":horizantal_distance,"turn_direction":turn_direction,"alt_command":alt_command,"Qbetween":Qbetween}
            self.corresponding_enemy_list[enemy["takim_numarasi"] - 1].append(result_listed)
            self.count = self.count +1
            if self.count >= 21:
                self.corresponding_enemy_list[enemy["takim_numarasi"] - 1].pop(0)
                fake_array = 0
                self.corresponding_enemy_list[enemy["takim_numarasi"] - 1].append(fake_array)
                self.count = 20
        #Trim the array
        b = 0
        check_flag = []
        for i in self.corresponding_enemy_list:
            if b !=0 and i == check_flag:
                del self.corresponding_enemy_list[b:]
                break
            b = b+1
        self.create_command()


    def create_command(self):
        characteristics_list = self.get_characteristics()
        in_range_count = 0
        in_range_list = [0,0,0]
        for enemy in self.corresponding_enemy_list:
            if enemy != []:
                if enemy[-1]["alt_command"] == "Dive":
                    alt_command = "Rise"
                elif enemy[-1]["alt_command"] == "Rise":
                    alt_command = "Dive"
                escape_angle=abs(90 - enemy[-1]["horizantal_angle"])

                if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("priority1") == True and characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("is_dangerous")== True:
                    speed = 75
                    if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("avoid_immediate") == True:
                        speed = 100
                    in_range_count = in_range_count + 1
                    in_range_list[0]=[escape_angle,alt_command,speed]
                elif characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("priority2") == True and characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("is_dangerous")== True:
                    speed = 75 
                    if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("avoid_immediate") == True:
                        speed = 100
                    in_range_count = in_range_count + 1
                    in_range_list[1]=[escape_angle,alt_command,speed]
                elif characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("priority3") == True and characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("is_dangerous")== True:
                    speed = 75
                    if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("avoid_immediate") == True:
                        speed = 100
                    in_range_count = in_range_count + 1
                    in_range_list[2]=[escape_angle,alt_command,speed]
                else : 
                    continue
        if in_range_count == 1:
            if enemy[-1]["turn_direction"] == "Medium Right":
                print("Turn {} to the left and {} and accelerate at speed %{} ".format(in_range_list[0][0],in_range_list[0][1],in_range_list[0][2]))
            elif enemy[-1]["turn_direction"] == "Medium Left":
                print("Turn {} to the right and {} and accelerate at speed %{} ".format(in_range_list[0][0],in_range_list[0][1],in_range_list[0][2]))
            elif enemy[-1]["turn_direction"] == "Strong Right":
                print("Turn {} to the right and {} and accelerate at speed %{} ".format(in_range_list[0][0],in_range_list[0][1],in_range_list[0][2]))
            elif enemy[-1]["turn_direction"] == "Strong Left":
                print("Turn {} to the left and {} and accelerate at speed %{} ".format(in_range_list[0][0],in_range_list[0][1],in_range_list[0][2]))
            else:
                print("{} and accelerate at speed %{} ".format(in_range_list[0][1],in_range_list[0][2]))
        elif in_range_count == 2:
            print("Slow down to the %10 speed and turn right")
        elif in_range_count == 3:
            print("Slow down to the %10 speed and turn right and dive")
        self.enemy_list.clear()
        self.is_initialized = False
                    
                
                
                
                

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
                    prev_distance_list = prev_distance_list |  {"enemy_id{}".format(enemy[0]["enemy_id"]):0}
            self.prev_list_initialized = True
        for enemy in self.corresponding_enemy_list:  
            horizantal_angle_change = 0
            total_angle_change = 0
            horizantal_distance_change = 0 
            
            if enemy != []:
                
                if enemy[-1] != 0:
                    horizantal_angle_change = enemy[-1]["horizantal_angle"] - horizantal_angle_change
                    """ total_angle_change = enemy[-1]["total_angle"] - total_angle_change """
                    horizantal_distance_change = enemy[-1]["horizantal_distance"] - prev_distance_list["enemy_id{}".format(enemy[-1]["enemy_id"])]
                    prev_distance_list["enemy_id{}".format(enemy[-1]["enemy_id"])] = enemy[-1]["horizantal_distance"]
                
                if enemy[-1]["horizantal_angle"] < 360:
                    if horizantal_distance_change >0:
                        is_approaching = False
                        is_watching = False
                        is_in_watch_list = False
                        is_dangerous = False
                        avoid_immediate = False
                    elif horizantal_distance_change < 0:
                        is_approaching = True
                        if enemy[-1]["Qbetween"] > 15 or enemy[-1]["Qbetween"] < -15:
                            is_in_watch_list = False
                            is_watching = True
                            is_dangerous = False
                            avoid_immediate = False
                        elif 25> enemy[-1]["Qbetween"] > 15 or -15 > enemy[-1]["Qbetween"] > -25 : 
                            is_in_watch_list = True
                            is_watching = True
                            is_dangerous = False
                            avoid_immediate = False
                        elif 15> enemy[-1]["Qbetween"]  or  enemy[-1]["Qbetween"] > -15 :
                            if enemy[-1]["horizantal_distance"] < 120:
                                is_dangerous = True
                                is_watching = True
                                is_in_watch_list = True
                                avoid_immediate = True
                            elif enemy[-1]["horizantal_distance"] < 200:
                                is_dangerous = True
                                is_watching = True
                                is_in_watch_list = True
                                avoid_immediate = False
                            else : 
                                is_watching = True
                                is_in_watch_list = True
                    temp_dict = {"is_approaching":is_approaching,"is_watching":is_watching,"is_in_watch_list":is_in_watch_list,"is_dangerous":is_dangerous,"avoid_immediate":avoid_immediate}
                    if self.sorted_list_counter <= 2 :
                        if enemy[-1]["enemy_id"] == sorted_distance_list[self.sorted_list_counter]["enemy_id"]:
                            
                            if self.sorted_list_counter == 0:
                                temp2_dict = {"priority1":True ,"priority2":False,"priority3":False }
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
        print(priority_attached_list)
        return behaviour_dict
     

    
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
        print(self.poly)
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
    def send_commands(self):
        self.angle_calc()
    def destination_estimate(self):
        pass
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
        global prev_coordinates_enemy
        enemy_raw_x=self.map_start_x - enemy_x
        enemy_raw_y= (self.map_end_y - enemy_y) * -1
        us_raw_x = self.map_start_x - us_x
        us_raw_y = (self.map_end_y - us_y) * -1
        Qdirection ,our_direction= self.get_direction_vector(us_x,us_y) 
        Qbetween = math.degrees(atan(abs(enemy_y - us_y)/abs(enemy_x - us_x)))
        Qenemy ,enemy_direction= self.get_direction_vector(enemy_raw_x,enemy_raw_y)
        if self.estimation_initialized == False:
            prev_coordinates_enemy = [(enemy_raw_x , enemy_raw_y),(us_raw_x , us_raw_y),Qenemy]
            self.estimation_initialized = True
        Qrotate= 0
        direction_x = enemy_x - us_x
        direction_y = enemy_y - us_y
        uDirection = "Right"
        if direction_x > 0 and direction_y >0:
            print("Enemy Region 1 direction")
            if our_direction == "Q1":
                if Qdirection>Qbetween:
                    uDirection = "Right"
                    Qrotate = Qdirection - Qbetween
                else:
                    uDirection = "Left"
                    Qrotate = Qbetween - Qdirection
            elif our_direction == "Q2":
                uDirection = "Medium Right"
                Qrotate = 180 - Qdirection - Qbetween
            elif our_direction == "Q3":
                if Qdirection >45:
                    uDirection = "Strong Right"
                    Qrotate = 180 -Qbetween + Qdirection
                else :
                    uDirection = "Strong Left"
                    Qrotate = 180 +Qbetween - Qdirection
            elif our_direction == "Q4":
                uDirection = "Medium Left"
                Qrotate = Qdirection +Qbetween
        elif direction_x <0 and direction_y >0:
            print("Enemy Region 2 direction")
            if our_direction == "Q1":
                uDirection = "Medium Left"
                Qrotate = 180 - Qbetween - Qdirection
            elif our_direction == "Q2":
                if abs(direction_x)<abs(direction_y):
                    uDirection = "Left"
                    Qrotate = Qdirection - Qbetween
                else:
                    uDirection = "Right"
                    Qrotate = Qbetween - Qdirection
            elif our_direction == "Q3":
                uDirection = "Medium Right"
                Qrotate = Qbetween + Qdirection
            elif our_direction == "Q4":
                if Qdirection >45:
                    uDirection = "Strong Right"
                    Qrotate = 180 - Qdirection + Qbetween
                else :
                    uDirection = "Strong Left"
                    Qrotate = 180 - Qbetween + Qdirection
        elif direction_x <0 and direction_y <0:
            print("Enemy Region 3 direction")
            if our_direction == "Q1":
                if Qdirection >45:
                    uDirection = "Strong Left"
                    Qrotate = 180 - Qdirection + Qbetween
                else :
                    uDirection = "Strong Right"
                    Qrotate = 180 - Qbetween + Qdirection
            elif our_direction == "Q2":
                uDirection = "Medium Left"
                Qrotate = Qbetween + Qdirection 
            elif our_direction == "Q3":
                if abs(direction_x)>abs(direction_y):
                    uDirection = "Left"
                    Qrotate = Qbetween - Qdirection
                else:
                    uDirection = "Right"
                    Qrotate = Qdirection - Qbetween
            elif our_direction == "Q4":
               uDirection = "Medium Right"
               Qrotate = 180 - Qbetween - Qdirection
        elif direction_x >0 and direction_y < 0:
            print("Enemy Region 4 direction")
            if our_direction == "Q1":
                uDirection = "Medium Right"
                Qrotate = Qbetween + Qdirection
            elif our_direction == "Q2": 
                if Qdirection >45:
                    uDirection = "Strong Right"
                    Qrotate = 180 - Qdirection + Qbetween
                else :
                    uDirection = "Strong Left"
                    Qrotate = 180 - Qbetween + Qdirection
            elif our_direction == "Q3":
                uDirection = "Medium Left"
                Qrotate = 180 - Qdirection - Qbetween
            elif our_direction == "Q4":
                if abs(direction_x)>abs(direction_y):
                    uDirection = "Right"
                    Qrotate = Qbetween - Qdirection
                else:
                    uDirection = "Left"
                    Qrotate = Qdirection - Qbetween
        diff_irtifa = rakip_irtifa - irtifa
        alt_command = "null"
        if diff_irtifa >0:
            alt_command = "Rise"
        else:
            alt_command = "Dive"
        horizontal_difference=geopy.distance.geodesic(self.enemy, self.us).meters
        error_rate_x ,error_rate_y= 10 , 10
        
        angle_error = (abs(Qenemy - prev_coordinates_enemy[2])/prev_coordinates_enemy[2]) * 100
        if angle_error < 5.1 :
            estimated_enemy_X = enemy_raw_x+(3*(enemy_raw_x - prev_coordinates_enemy[0][0]))
            estimated_enemy_y = enemy_raw_y+(3*(enemy_raw_y - prev_coordinates_enemy[0][1]))
            estimated_us_x = us_raw_x+(3*(us_raw_x - prev_coordinates_enemy[1][0]))
            estimated_us_y = us_raw_y+(3*(us_raw_y - prev_coordinates_enemy[1][1]))
            if estimated_enemy_X < 0 and estimated_us_x > 0 and estimated_enemy_y > 0 and estimated_us_y > 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max((estimated_us_x + abs(estimated_enemy_X - estimated_us_x)),estimated_us_x))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max(estimated_enemy_y,estimated_us_y)) * 100
            elif estimated_enemy_X > 0 and estimated_us_x <0 and estimated_enemy_y > 0 and estimated_us_y > 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max(estimated_enemy_X,(estimated_enemy_X + abs(estimated_enemy_X - estimated_us_x))))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max(estimated_enemy_y,estimated_us_y)) * 100
            elif estimated_enemy_X > 0 and estimated_us_x > 0 and estimated_enemy_y < 0 and estimated_us_y > 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max(estimated_enemy_X,estimated_us_x))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max((estimated_us_y + abs(estimated_enemy_y - estimated_us_y)),estimated_us_y)) * 100
            elif estimated_enemy_X > 0 and estimated_us_x > 0 and estimated_enemy_y > 0 and estimated_us_y < 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max(estimated_enemy_X,estimated_us_x))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max(estimated_enemy_y,(estimated_enemy_y + abs(estimated_enemy_y - estimated_us_y)))) * 100
            elif estimated_enemy_X > 0 and estimated_us_x > 0 and estimated_enemy_y > 0 and estimated_us_y > 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max(estimated_enemy_X,estimated_us_x)) * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max(estimated_enemy_y,estimated_us_y)) * 100
            elif estimated_enemy_X < 0 and estimated_us_x <0 and estimated_enemy_y > 0 and estimated_us_y > 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max(estimated_enemy_X * -1 , estimated_us_x * -1))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max(estimated_enemy_y,estimated_us_y)) * 100
            elif estimated_enemy_X > 0 and estimated_us_x > 0 and estimated_enemy_y < 0 and estimated_us_y < 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max(estimated_enemy_X,estimated_us_x))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max(estimated_enemy_y * -1 ,estimated_us_y * -1 )) * 100
            elif estimated_enemy_X > 0 and estimated_us_x < 0 and estimated_enemy_y > 0 and estimated_us_y < 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max(estimated_enemy_X,(estimated_enemy_X + abs(estimated_enemy_X - estimated_us_x))))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max(estimated_enemy_y,(estimated_enemy_y + abs(estimated_enemy_y - estimated_us_y)))) * 100
            elif estimated_enemy_X < 0 and estimated_us_x > 0 and estimated_enemy_y < 0 and estimated_us_y > 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max((estimated_us_x + abs(estimated_enemy_X - estimated_us_x)),estimated_us_x))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max((estimated_us_y + abs(estimated_enemy_y - estimated_us_y)),estimated_us_y)) * 100
            elif estimated_enemy_X < 0 and estimated_us_x > 0 and estimated_enemy_y > 0 and estimated_us_y < 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max((estimated_us_x + abs(estimated_enemy_X - estimated_us_x)),estimated_us_x))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max(estimated_enemy_y,(estimated_enemy_y + abs(estimated_enemy_y - estimated_us_y)))) * 100
            elif estimated_enemy_X > 0 and estimated_us_x < 0 and estimated_enemy_y < 0 and estimated_us_y > 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max(estimated_enemy_X,(estimated_enemy_X + abs(estimated_enemy_X - estimated_us_x))))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max((estimated_us_y + abs(estimated_enemy_y - estimated_us_y)),estimated_us_y)) * 100
            elif estimated_enemy_X < 0 and estimated_us_x < 0 and estimated_enemy_y < 0 and estimated_us_y > 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max((estimated_us_x + abs(estimated_enemy_X - estimated_us_x)),(estimated_enemy_X + abs(estimated_enemy_X - estimated_us_x))))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max((estimated_us_y + abs(estimated_enemy_y - estimated_us_y)),estimated_us_y)) * 100
            elif estimated_enemy_X < 0 and estimated_us_x < 0 and estimated_enemy_y > 0 and estimated_us_y < 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max((estimated_us_x + abs(estimated_enemy_X - estimated_us_x)),(estimated_enemy_X + abs(estimated_enemy_X - estimated_us_x))))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max(estimated_enemy_y,(estimated_enemy_y + abs(estimated_enemy_y - estimated_us_y)))) * 100
            elif estimated_enemy_X < 0 and estimated_us_x > 0 and estimated_enemy_y < 0 and estimated_us_y < 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max((estimated_us_x + abs(estimated_enemy_X - estimated_us_x)),estimated_us_x))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max((estimated_us_y + abs(estimated_enemy_y - estimated_us_y)),(estimated_enemy_y + abs(estimated_enemy_y - estimated_us_y)))) * 100
            elif estimated_enemy_X > 0 and estimated_us_x < 0 and estimated_enemy_y < 0 and estimated_us_y < 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max(estimated_enemy_X,(estimated_enemy_X + abs(estimated_enemy_X - estimated_us_x))))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max((estimated_us_y + abs(estimated_enemy_y - estimated_us_y)),(estimated_enemy_y + abs(estimated_enemy_y - estimated_us_y)))) * 100
            elif estimated_enemy_X < 0 and estimated_us_x < 0 and estimated_enemy_y < 0 and estimated_us_y < 0:
                error_rate_x = (abs(estimated_enemy_X - estimated_us_x)/max((estimated_us_x + abs(estimated_enemy_X - estimated_us_x)),(estimated_enemy_X + abs(estimated_enemy_X - estimated_us_x))))  * 100
                error_rate_y = (abs(estimated_enemy_y - estimated_us_y)/max((estimated_us_y + abs(estimated_enemy_y - estimated_us_y)),(estimated_enemy_y + abs(estimated_enemy_y - estimated_us_y)))) * 100

        if error_rate_x < 5 and error_rate_y < 5:
            print("Collision Ahead")
        prev_coordinates_enemy=[(enemy_raw_x,enemy_raw_y),(us_raw_x,us_raw_y),Qenemy]
        #Difference in total angle 
        angle = ((enemy_x * us_x)+(enemy_y*us_y)+(rakip_irtifa*irtifa))/(sqrt((enemy_x ** 2)+(enemy_y ** 2)+(rakip_irtifa **2)) * sqrt((us_x ** 2)+(us_y ** 2)+(irtifa ** 2)))
        angle_diff=math.degrees(acos(angle))
        return  Qrotate , horizontal_difference , uDirection ,alt_command , Qbetween ,direction_x , direction_y ,



telemetry_data=[{
                            "takim_numarasi": 1,
                            "IHA_enlem": 39.855008,
                            "IHA_boylam": 32.781415,
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
                            "IHA_enlem": 39.855805,
                            "IHA_boylam": 32.782447,
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
                            "IHA_enlem": 39.855800,
                            "IHA_boylam": 32.779700,
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
                            }
                            ,{
                            "takim_numarasi": 4,
                            "IHA_enlem": 39.854099,
                            "IHA_boylam": 32.779170,
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
                            "IHA_enlem": 39.853818,
                            "IHA_boylam": 32.783296,
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
a = [{
                            "takim_numarasi": 1,
                            "IHA_enlem": 39.855008,
                            "IHA_boylam": 32.781415,
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
                            },{
                            "takim_numarasi": 2,
                            "IHA_enlem": 39.855660,
                            "IHA_boylam": 32.782955,
                            "IHA_irtifa": 98,
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
                            "IHA_enlem": 39.855460,
                            "IHA_boylam": 32.779308,
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
                            "IHA_enlem": 39.854354,
                            "IHA_boylam": 32.779782,
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
                            "IHA_enlem": 39.853660,
                            "IHA_boylam": 32.782899,
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
                            }]
b = [{
                            "takim_numarasi": 1,
                            "IHA_enlem": 39.855008,
                            "IHA_boylam": 32.781415,
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
                            },{
                            "takim_numarasi": 2,
                            "IHA_enlem":  39.856986, 
                            "IHA_boylam": 32.781013,
                            "IHA_irtifa": 103,
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
                            "IHA_enlem": 39.855298,
                            "IHA_boylam": 32.779571,
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
                            "IHA_enlem": 39.854643,
                            "IHA_boylam": 32.780200,
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
                            "IHA_enlem": 39.854244,
                            "IHA_boylam": 32.781736,
                            "IHA_irtifa": 110,
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
c = [{
                            "takim_numarasi": 1,
                            "IHA_enlem": 39.855008,
                            "IHA_boylam": 32.781415,
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
                            },{
                            "takim_numarasi": 2,
                            "IHA_enlem":  39.85603012392855, 
                            "IHA_boylam": 32.78145270553317,
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
                            "IHA_enlem": 39.855298,
                            "IHA_boylam": 32.779571,
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
                            "IHA_enlem": 39.854643,
                            "IHA_boylam": 32.780200,
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
                            "IHA_enlem": 39.853569,
                            "IHA_boylam": 32.782337,
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
telemetry_list = [telemetry_data,a,b,c]
import time
start = datetime.now()

thread = threading.Thread(target=Window,args=())
thread.start()
startpoint = [39.854818,32.781299,100]
our_location = [[39.855008,32.781415,100],[39.85512328601099, 32.78198362544963,100],[39.85517270305381, 32.78279901694268,100],[39.85471971216288, 32.78420449438465,100]]
drive = Decider(team_number=1,starting_point=startpoint)
for i in range(4):
    drive.flight_controller(incoming_data=telemetry_list[i],our_location=our_location[i])
    time.sleep(0.987)
print(datetime.now() - start)
    
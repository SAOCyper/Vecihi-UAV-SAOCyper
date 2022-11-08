import geopy.distance
import math
from math import sin, cos, sqrt, atan2, radians ,acos ,degrees

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
        pass

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
        #Difference angle in horizantal 
        diff_x = abs(enemy_x - us_x)
        diif_y = abs(enemy_y - us_y)
        horizantal_angle = math.degrees(acos(diff_x/(sqrt((diff_x ** 2)+(diif_y ** 2)))))
        
        diff_irtifa = abs(rakip_irtifa - irtifa)
        horizontal_difference=geopy.distance.geodesic(self.enemy, self.us).m
        #Difference in total angle 
        angle = ((enemy_x * us_x)+(enemy_y*us_y)+(rakip_irtifa*irtifa))/(sqrt((enemy_x ** 2)+(enemy_y ** 2)+(rakip_irtifa **2)) * sqrt((us_x ** 2)+(us_y ** 2)+(irtifa ** 2)))
        angle_diff=math.degrees(acos(angle))
        return angle_diff , horizantal_angle

auto=AutoPilot()
auto.angle_calc_different_method(43.576546,22.385421,100,43.574352,22.37245421,145)
auto.angle_calc(43.576546,22.385421,100,43.594352,22.37245421,145)
    
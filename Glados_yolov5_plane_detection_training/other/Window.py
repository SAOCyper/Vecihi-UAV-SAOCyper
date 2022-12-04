import tkinter
import tkintermapview
import os
from math import *
import math
from pyproj import Geod
import threading,sys
sys.path.insert(1, r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\src\modules')
import telemetry_data
window_initialized = False
prev_coordinates = []
enemy_prev_list = []
previous_location_list = []
coordinates_prev = (0,0)
p=0
def new_location_set(distance,angle,location:list,lat_change,lon_change,rotation):
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

def create_polygon(map_widget):
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
        map_widget.set_polygon(position_list=edges)
        """ for i in range(len(points)):
            map_widget.set_marker(points[i][0],points[i][1])
        for i in range(len(side_points)):
            map_widget.set_marker(side_points[i][0],side_points[i][1]) """
        map_widget.set_path(position_list=[z_middle,points[0]],color="red",width = 1)
        map_widget.set_path(position_list=[z_middle,points[1]],color="red",width = 1)
        map_widget.set_path(position_list=[z_middle,points[2]],color="red",width = 1)
        map_widget.set_path(position_list=[z_middle,points[3]],color="red",width = 1)

        map_widget.set_path(position_list=[q1_middle,side_points[0]],color="red",width = 1)
        map_widget.set_path(position_list=[q1_middle,side_points[1]],color="red",width = 1)
        map_widget.set_path(position_list=[q1_middle,side_points[2]],color="red",width = 1)
        map_widget.set_path(position_list=[q1_middle,side_points[3]],color="red",width = 1)

        map_widget.set_path(position_list=[q2_middle,side_points[4]],color="red",width = 1)
        map_widget.set_path(position_list=[q2_middle,side_points[3]],color="red",width = 1)
        map_widget.set_path(position_list=[q2_middle,side_points[5]],color="red",width = 1)
        map_widget.set_path(position_list=[q2_middle,side_points[6]],color="red",width = 1)

        map_widget.set_path(position_list=[q3_middle,side_points[5]],color="red",width = 1)
        map_widget.set_path(position_list=[q3_middle,side_points[7]],color="red",width = 1)
        map_widget.set_path(position_list=[q3_middle,side_points[8]],color="red",width = 1)
        map_widget.set_path(position_list=[q3_middle,side_points[9]],color="red",width = 1)

        map_widget.set_path(position_list=[q4_middle,side_points[2]],color="red",width = 1)
        map_widget.set_path(position_list=[q4_middle,side_points[10]],color="red",width = 1)
        map_widget.set_path(position_list=[q4_middle,side_points[11]],color="red",width = 1)
        map_widget.set_path(position_list=[q4_middle,side_points[7]],color="red",width = 1)
def draw_planes(map_widget,enemy_list,enemy_next_list,team_number):
        geodesic = Geod(ellps='WGS84')
        #print(enemy_list)
        global enemy_prev_list
        global coordinates_prev
        global window_initialized
        if window_initialized == False :
            a = 0
            for enemy in enemy_list :
                if enemy == []:
                    a = a +1
                    enemy_prev_list.pop(a)
                a = a +1
            enemy_prev_list = enemy_list
            window_initialized = True
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
            left_line=new_location_set(distance=100,angle=line_rotation_left,location=coordinates,lat_change=lat_change,lon_change=lon_change,rotation=rotation)
            right_line = new_location_set(distance=100,angle=line_rotation_right,location=coordinates,lat_change=lat_change,lon_change=lon_change,rotation=rotation)
            fill_color = "red"
            if team_number == enemy[i]["takim_numarasi"]:
                fill_color = "blue"
            search_edges = [left_line,right_line,coordinates]
            map_widget.set_path(position_list=[coordinates_prev,coordinates],color="blue",width = 2)
            map_widget.set_path(position_list=[coordinates,left_line],color="blue",width = 2)
            map_widget.set_path(position_list=[coordinates,right_line],color="blue",width = 2)
            i = i +1
            
        enemy_prev_list = enemy_list     



def create_window(enemy_list,team_number):
    mainWindow = tkinter.Tk()

    mainWindow.title("Grid Demo")
    mainWindow.geometry('1080x680+200+100')
    mainWindow['padx'] = 8

    label= tkinter.Label(mainWindow, text="Tkinter Grid Demo")
    label.grid(row=0, column=0, columnspan=3)

    mainWindow.columnconfigure(0, weight=100)
    mainWindow.columnconfigure(1, weight=1)
    mainWindow.columnconfigure(2, weight=1000)
    mainWindow.columnconfigure(3, weight=600)
    mainWindow.columnconfigure(4, weight=1000)
    mainWindow.rowconfigure(0, weight=1)
    mainWindow.rowconfigure(1, weight=10)
    mainWindow.rowconfigure(2, weight=1)
    mainWindow.rowconfigure(3, weight=3)
    mainWindow.rowconfigure(4, weight=3)

    map_widget = tkintermapview.TkinterMapView(mainWindow,width=640,height=480,corner_radius=10)
    map_widget.set_position(39.856398, 32.780181)
    map_widget.set_zoom(16)
    create_polygon(map_widget)
    for i in range(len(telemetry_list)):
        thread = threading.Thread(target=draw_planes,args=(map_widget,[telemetry_list[i]],[telemetry_list[i+1]],team_number))
        thread.start()
    map_widget.grid(row=1, column=0, sticky='nsew', rowspan=2)
    map_widget.config(border=2, relief='sunken')
    listScroll = tkinter.Scrollbar(mainWindow, orient=tkinter.VERTICAL)
    listScroll.grid(row=1, column=1, sticky='nsw', rowspan=2)
    #draw_planes(map_widget)

    # frame for the radio buttons
    optionFrame = tkinter.LabelFrame(mainWindow, text="File Details")
    optionFrame.grid(row=1, column=2, sticky='ne')

    rbValue = tkinter.IntVar()
    rbValue.set(1)
    # Radio buttons
    radio1 = tkinter.Radiobutton(optionFrame, text="Filename", value=1, variable=rbValue)
    radio2 = tkinter.Radiobutton(optionFrame, text="Path", value=2, variable=rbValue)
    radio3 = tkinter.Radiobutton(optionFrame, text="Timestamp", value=3, variable=rbValue)
    radio1.grid(row=0, column=0, sticky='w')
    radio2.grid(row=1, column=0, sticky='w')
    radio3.grid(row=2, column=0, sticky='w')

    # Widget to display the result
    resultLabel = tkinter.Label(mainWindow, text="Result")
    resultLabel.grid(row=2, column=2, sticky='nw')
    result = tkinter.Entry(mainWindow)
    result.grid(row=2, column=2, sticky='sw')

    # Frame for the time spinners
    timeFrame = tkinter.LabelFrame(mainWindow, text="Time")
    timeFrame.grid(row=3, column=0, sticky='new')
    # Time spinners
    hourSpinner = tkinter.Spinbox(timeFrame, width=2, values=tuple(range(0, 24)))
    minuteSpinner = tkinter.Spinbox(timeFrame, width=2, from_=0, to=59)
    secondSpinner = tkinter.Spinbox(timeFrame, width=2, from_=0, to=59)
    hourSpinner.grid(row=0, column=0)
    tkinter.Label(timeFrame, text=':').grid(row=0, column=1)
    minuteSpinner.grid(row=0, column=2)
    tkinter.Label(timeFrame, text=':').grid(row=0, column=3)
    secondSpinner.grid(row=0, column=4)
    timeFrame['padx'] = 36

    # Frame for the date spinners
    dateFrame = tkinter.Frame(mainWindow)
    dateFrame.grid(row=4, column=0, sticky='new')
    # Date labels
    dayLabel = tkinter.Label(dateFrame, text="Day")
    monthLabel = tkinter.Label(dateFrame, text="Month")
    yearLabel = tkinter.Label(dateFrame, text="Year")
    dayLabel.grid(row=0, column=0, sticky='w')
    monthLabel.grid(row=0, column=1, sticky='w')
    yearLabel.grid(row=0, column=2, sticky='w')
    # Date spinners
    daySpin = tkinter.Spinbox(dateFrame, width=5, from_=1, to=31)
    monthSpin = tkinter.Spinbox(dateFrame, width=5, values=("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"))
    yearSpin = tkinter.Spinbox(dateFrame, width=5, from_=2000, to=2099)
    daySpin.grid(row=1, column=0)
    monthSpin.grid(row=1, column=1)
    yearSpin.grid(row=1, column=2)

    # Buttons
    okButton = tkinter.Button(mainWindow, text="OK")
    cancelButton = tkinter.Button(mainWindow, text="Cancel", command=mainWindow.destroy)
    okButton.grid(row=4, column=3, sticky='e')
    cancelButton.grid(row=4, column=4, sticky='w')

    mainWindow.mainloop()

    print(rbValue.get())


if __name__ == "__main__":
    telemetry_list = telemetry_data.get_data()
    team_number = 1
    create_window(telemetry_list,team_number)
    
        
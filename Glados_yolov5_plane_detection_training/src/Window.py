import tkinter,socket, pickle
import tkintermapview
import os
from math import *
import math
from pyproj import Geod
import threading,sys,time
import sys
import socket
import selectors
import traceback

sys.path.insert(1, r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\src\modules')
import telemetry_data
import libclient
team_number = 1
sel = 0
enemy_list  = []
in_waiting = False
window_initialized = False
p = 0
prev_drawing = []
drawing_initialized = False

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
        sent = create_post_value(value=value)
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

def attempt_reconnect(func,*args,**kwargs):
        MAX_RETRY=2
        for i in range(MAX_RETRY):
            try:
                return_value=func(*args,**kwargs)
                break
            except Exception as e:
                print("error"+str(e))
                return_value=e
                time.sleep(1)
        return return_value


def start_client():
    global enemy_list
    global prev_drawing
    global drawing_initialized
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server
    addr = (HOST, PORT)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.connect_ex(addr)
        while True:
            s.sendall(b"200")
            data = s.recv(4096)
            if not data:
                break
            
            #data = json.loads(data)
            enemy_list = pickle.loads(data)
            if drawing_initialized == False:
                if enemy_list == [0,0]:
                    drawing_initialized = False
                else:
                    for i in range(len(enemy_list)):
                        prev_drawing.append([])
                        for j in enemy_list[i]:
                            prev_drawing[i].append([0,0,0]) 
                    drawing_initialized = True 
            print(f"Received {enemy_list!r}")
            if enemy_list != [0,0]:
                break
        

class Window():

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

    def __get_data(self):

        global enemy_list
        global prev_drawing
        global drawing_initialized
        action = "get"
        value = "/api/telemetri_gonder"
        host = "127.0.0.1"
        port = 65432
        request = create_request(action, value)
        start_connection(host, port,action,request)

        try:
            while True:
                events = sel.select(timeout=0)
                for key, mask in events:
                    message = key.data
                    try:
                        enemy_list = message.process_events(mask)
                        if drawing_initialized == False and enemy_list != 0:
                            if enemy_list == [0,0]:
                                drawing_initialized = False
                            else:
                                for i in range(len(enemy_list)):
                                    prev_drawing.append([])
                                    for j in enemy_list[i]:
                                        prev_drawing[i].append([0,0,0]) 
                                drawing_initialized = True
                    except Exception:
                        print(
                            f"Main: Error: Exception for {message.addr}:\n"
                            f"{traceback.format_exc()}"
                        )
                        message.close()
                # Check for a socket being monitored to continue.
                if not sel.get_map():
                    break
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            sel.close()

    def _get_data(self):
        global enemy_list
        global prev_drawing
        global drawing_initialized
        HOST = "127.0.0.1"  # The server's hostname or IP address
        PORT = 65432  # The port used by the server
        addr = (HOST, PORT)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
            self.s.connect((HOST, PORT))
            self.s.connect_ex(addr)
            while True:
                    self.s.sendall(b"200")
                    data = self.s.recv(4096)
                    if not data:
                        print("Connection Closed")
                        self.s.close()
                        break
                    
                    #data = json.loads(data)
                    enemy_list = pickle.loads(data)
                    if drawing_initialized == False:
                        if enemy_list == [0,0]:
                            drawing_initialized = False
                        else:
                            for i in range(len(enemy_list)):
                                prev_drawing.append([])
                                for j in enemy_list[i]:
                                    prev_drawing[i].append([0,0,0]) 
                            drawing_initialized = True 
                    print(f"Received {enemy_list!r}")
                    if enemy_list != [0,0]:
                        print("Connection Closed")
                        self.s.close()
                        break

    def __init__(self):
        self.window_initialized = False
        
        self.mainWindow = tkinter.Tk()
        self.mainWindow.title("Grid Demo")
        self.mainWindow.geometry('1080x680+200+100')
        self.mainWindow['padx'] = 8

        label= tkinter.Label(self.mainWindow, text="Tkinter Grid Demo")
        label.grid(row=0, column=0, columnspan=3)

        self.mainWindow.columnconfigure(0, weight=100)
        self.mainWindow.columnconfigure(1, weight=1)
        self.mainWindow.columnconfigure(2, weight=1000)
        self.mainWindow.columnconfigure(3, weight=600)
        self.mainWindow.columnconfigure(4, weight=1000)
        self.mainWindow.rowconfigure(0, weight=1)
        self.mainWindow.rowconfigure(1, weight=10)
        self.mainWindow.rowconfigure(2, weight=1)
        self.mainWindow.rowconfigure(3, weight=3)
        self.mainWindow.rowconfigure(4, weight=3)

        self.map_widget = tkintermapview.TkinterMapView(self.mainWindow,width=640,height=480,corner_radius=10)
        self.map_widget.set_position(39.856398, 32.780181)
        self.map_widget.set_zoom(16)
        self.create_polygon()
        self.map_widget.grid(row=1, column=0, sticky='nsew', rowspan=2)
        self.map_widget.config(border=2, relief='sunken')
        listScroll = tkinter.Scrollbar(self.mainWindow, orient=tkinter.VERTICAL)
        listScroll.grid(row=1, column=1, sticky='nsw', rowspan=2)
        
        
        # frame for the radio buttons
        optionFrame = tkinter.LabelFrame(self.mainWindow, text="File Details")
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
        resultLabel = tkinter.Label(self.mainWindow, text="Result")
        resultLabel.grid(row=2, column=2, sticky='nw')
        result = tkinter.Entry(self.mainWindow)
        result.grid(row=2, column=2, sticky='sw')

        # Frame for the time spinners
        timeFrame = tkinter.LabelFrame(self.mainWindow, text="Time")
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
        dateFrame = tkinter.Frame(self.mainWindow)
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
        okButton = tkinter.Button(self.mainWindow, text="OK")
        cancelButton = tkinter.Button(self.mainWindow, text="Cancel", command=self.mainWindow.destroy)
        okButton.grid(row=4, column=3, sticky='e')
        cancelButton.grid(row=4, column=4, sticky='w')
        global team_number
        self.map_widget.after(1000, self.update,team_number)
    

    def run(self):
        self.mainWindow.mainloop()

    def update(self,team_number):
        geodesic = Geod(ellps='WGS84')
        self.__get_data()
        global enemy_prev_list
        global coordinates_prev
        global window_initialized
        global in_waiting
        global enemy_list
        global prev_drawing
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
        enemy_next_list=enemy_list[1]
        enemy = enemy_list[0]
        enemy_prev2 = enemy_prev_list[1]
        enemy_prev1 = enemy_prev_list[0]
        if enemy[0] != 0:
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

                rot=geodesic.inv(coordinates_prev[1],coordinates_prev[0],coordinates[1],coordinates[0])
                left_line=Window._set_watch_points(distance=80,angle=line_rotation_left,location=coordinates,lat_change=lat_change,lon_change=lon_change,rotation=rotation)
                right_line = Window._set_watch_points(distance=80,angle=line_rotation_right,location=coordinates,lat_change=lat_change,lon_change=lon_change,rotation=rotation)
                left_line2 = Window._set_watch_points(distance=80,angle=line_rotation_left1,location=coordinates1,lat_change=lat_change1,lon_change=lon_change1,rotation=rotation1)
                right_line2 =  Window._set_watch_points(distance=80,angle=line_rotation_right1,location=coordinates1,lat_change=lat_change1,lon_change=lon_change1,rotation=rotation1)
                fill_color = "red"
                if team_number == enemy[a]["takim_numarasi"]:
                    fill_color = "blue"
                search_edges = [left_line,right_line,coordinates]
                search_edges1 = [left_line2,right_line2,coordinates1]
                prev_drawing[1][a][0] =  self.map_widget.set_path(position_list=[coordinates_prev,coordinates],color="blue",width = 2)
                prev_drawing[1][a][1] = self.map_widget.set_path(position_list=[coordinates,left_line],color="blue",width = 2)
                prev_drawing[1][a][2] = self.map_widget.set_path(position_list=[coordinates,right_line],color="blue",width = 2)
                prev_drawing[0][a][0] =  self.map_widget.set_path(position_list=[coordinates_prev1,coordinates1],color="blue",width = 2)
                prev_drawing[0][a][1] = self.map_widget.set_polygon(position_list=search_edges,fill_color = "red",border_width = 3)
                #prev_drawing[0][a][1] = self.map_widget.set_path(position_list=[coordinates1,left_line2],color="blue",width = 2)
                #prev_drawing[0][a][2] = self.map_widget.set_path(position_list=[coordinates1,right_line2],color="blue",width = 2)
                #prev_drawing[0][a][1] = 0
                prev_drawing[0][a][2] = 0
                
                i = i +1
             
        enemy_prev_list = enemy_list
        self.map_widget.after(1000, self.update,team_number)

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




if __name__ == "__main__":
    window = Window()
    #client_thread = threading.Thread(target=start_client)
    #client_thread.start()
    window.run()
    
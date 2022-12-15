import tkinter,socket, pickle,tkintermapview,os,socket,sys,selectors,traceback,threading,sys,time,math,geopy.distance,cv2
sys.path.insert(1, r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\src\modules')
import telemetry_data
import libclient
from math import sin, cos, sqrt, atan2, radians ,acos ,degrees,atan,asin
from datetime import datetime
import numpy as np
from numpy import mean
from shapely.geometry import Polygon
from selenium import webdriver
from pyproj import Geod
from PIL import ImageTk, Image
from geographiclib.geodesic import Geodesic
import matplotlib.pyplot as plt
import time
from scipy.interpolate import *
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from pathlib import Path
#Camera Global Paremeters
frame = 0
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
#GUI Parameters
sel = 0
in_waiting = False
our_telemetry = 0
window_initialized = False
prev_drawing = []
drawing_initialized = False
#Localizasyon Parameters
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
class EscapeParameters:
    def __init__(self):
        pass
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
            
class Camera():
    @staticmethod
    def _GPS_Saati():
        time_format = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        splitted = time_format.split(":")
        splitted1 = splitted[2].split('.')
        gps_saat = {"saat":splitted[0],"dakika":splitted[1],"saniye":splitted1[0],"milisaniye":splitted1[1]}
        return gps_saat
    def __init__(self):    
        self.trained_face_data = cv2.CascadeClassifier(r'C:\CYCLOP\GLADOS\haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)  
        self.recorder = cv2.VideoWriter('output.mp4',cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 30,(int(self.cap.get(3)),int(self.cap.get(4))))
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
    
        #cv2.putText(frame,str(angD),(pt1[0]-40,pt1[1]-20),cv2.FONT_HERSHEY_COMPLEX,
                    #1.5,(0,0,255),2)
        return angD
    def detect(self):
        while True:
                # Capture frame-by-frame
                t0 = time.time()
                global frame , start , kilitlenme_sayısı ,kilitlenme ,diff_info ,hedef_merkez_x,hedef_merkez_y,başlangıç_zamanı,bitiş_zamanı
                ret, frame = self.cap.read()
                rows,cols,_ =frame.shape
                xmedium = int(cols/2)
                y_medium = int(rows/2)
                hitbox_right = int(cols - (cols/4))
                hitbox_left = int(cols/4)
                hitbox_up = int(rows/10)
                hitbox_down = int(rows - (rows/10))
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
                    for (x, y, w, h) in faces:
                        #print(x,y,w,h)
                        success = False
                        roi_gray = gray[y:y+h, x:x+w] #(ycord_start, ycord_end)
                        roi_color = frame[y:y+h, x:x+w]
                        end_cord_x = x + w
                        end_cord_y = y + h
                        distance = self.distance_finder(self.focal_length_measured,self.KNOWN_WIDTH,w)
                        #print("Distance is {} cm".format(distance))
                        framemid_x = int((end_cord_x + x)/2)
                        framemid_y = int((end_cord_y + y)/2)
                        dikey = ((end_cord_y - y)/rows)*100
                        yatay = ((end_cord_x - x)/cols)*100
                        point_list = [(hitbox_midpointx,hitbox_midpointy),(framemid_x,framemid_y),(hitbox_midpointx-1,0)]
                        angle = self.get_angle(point_list)
                        print(angle)
                        cv2.line(frame,(hitbox_midpointx,hitbox_midpointy),(framemid_x,framemid_y),color = (255,255,255),thickness=2)
                        cv2.rectangle(frame, (x, y), (end_cord_x, end_cord_y), color=(0, 0, 255), thickness=2)
                        cv2.putText(frame,text="Dikey = %{:.2f}".format(dikey),org=(end_cord_x+10, y+15),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(22,159,230),thickness=2,lineType=cv2.LINE_AA)
                        cv2.putText(frame,text="Yatay = %{:.2f}".format(yatay),org=(end_cord_x-70, y-15),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(22,159,2230),thickness=2,lineType=cv2.LINE_AA)
                        if (x > hitbox_left and end_cord_x < hitbox_right) and (y > hitbox_up and end_cord_y < hitbox_down):
                            if ( yatay > 5) and ( dikey > 5):
                                if start == 0:
                                    start = datetime.now()
                                    başlangıç_zamanı = Camera._GPS_Saati()
                                diff = (datetime.now() - start).seconds
                                if diff == 2:
                                    kilitlenme =False
                                if diff == 4:
                                    hedef_merkez_x = int((x+x+w)/2)
                                    hedef_merkez_y = int((y+y+h)/2)
                                    bitiş_zamanı = Camera._GPS_Saati()
                                    kilitlenme_sayısı = kilitlenme_sayısı +1 
                                    success = True
                                    kilitlenme = True
                                    start = 0
                                    print("Kilitlenme Sayısı:{}".format(kilitlenme_sayısı))
                                if success == True : 
                                    #Send data to server
                                    pass
                                
                                cv2.putText(frame,text="{} saniye".format(diff),org=(20,30),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(0,255,0),thickness=1,lineType=cv2.LINE_AA)
                                if kilitlenme == True:
                                    cv2.putText(frame,text="Locking Success!",org=(20,50),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(0,255,0),thickness=1,lineType=cv2.LINE_AA)
                                
                            else:
                                start = 0
                                kilitlenme = False
                        else:
                            start = 0
                            kilitlenme = False
                else : 
                    start = 0
                    kilitlenme = False
                # Display the resulting frame
                t = time.time()-t0
                self.fpsArray.append(1/t)
                averageFPS = mean(self.fpsArray)
                cv2.putText(frame,'FPS:' + str(averageFPS)[:4], (510,20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 1, cv2.LINE_AA)
                self.recorder.write(frame)
                del self.fpsArray[:-180]
                cv2.imshow('frame',frame)
                if cv2.waitKey(20) & 0xFF == ord('q'):
                    for i in range(3):
                        print("....CLOSING CAMERA in {} second ....".format(3-i))
                        time.sleep(1)
                    break
        # When everything done, release the capture
        self.cap.release()
        cv2.destroyAllWindows()
class Window():
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
        self.time_label.config(text="Sunucu Saati:{}".format(time_format),font=("Arial",18))
        self.time_label.after(10,self._time)

    def _telemetry_label(self):
        global our_telemetry
        self.telemetry_label.config(text = our_telemetry,font=("Arial",16))
        self.telemetry_label.after(10,self._telemetry_label)
    def __get_data(self):
        global enemy_list
        global prev_drawing
        global drawing_initialized
        action = "get"
        value = "/api/telemetri_gonder"
        host = "127.0.0.1"
        port = 65432
        request = ServerConnection.create_request(action, value)
        ServerConnection.start_connection(host, port,action,request)
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
    def _getoptions(self):
        selected_option = self.options.get()
        return selected_option
    def _getcamera(self):
        cap = cv2.VideoCapture(0)
        ret , frame = cap.read()
        cv2.imshow('frame',frame)
        self.camera.after(10,self._getcamera)
    def __init__(self):
        self.window_initialized = False
        
        self.mainWindow = tkinter.Tk()
        self.mainWindow.title("HÜMA VECİHİ SİHA PANEL")
        self.mainWindow.geometry('1240x750')
        self.mainWindow['padx'] = 8

        label= tkinter.Label(self.mainWindow, text="Vecihi HÜMA SİHA",font=("Arial",25))
        label.grid(row=0, column=0, columnspan=3)

        self.mainWindow.columnconfigure(0, weight=100)
        self.mainWindow.columnconfigure(1, weight=1)
        self.mainWindow.columnconfigure(2, weight=1000)
        self.mainWindow.columnconfigure(3, weight=600)
        self.mainWindow.columnconfigure(4, weight=1000)
        self.mainWindow.rowconfigure(0, weight=1)
        self.mainWindow.rowconfigure(1, weight=10)
        self.mainWindow.rowconfigure(2, weight=10)
        self.mainWindow.rowconfigure(3, weight=5)
        self.mainWindow.rowconfigure(4, weight=3)
        self.mainWindow.rowconfigure(5, weight=3)
        self.mainWindow.rowconfigure(6, weight=3)

        self.map_widget = tkintermapview.TkinterMapView(self.mainWindow,width=640,height=480,corner_radius=10)
        self.map_widget.set_position(39.856398, 32.780181)
        self.map_widget.set_zoom(16)
        self.create_polygon()
        self.map_widget.grid(row=1, column=0, sticky='nsew', rowspan=2)
        self.map_widget.config(border=2, relief='sunken')
        listScroll = tkinter.Scrollbar(self.mainWindow, orient=tkinter.VERTICAL)
        listScroll.grid(row=1, column=1, sticky='nsw', rowspan=2)

        # Create the list of options
        options_list = ["Otonom Kalkış", "Otonom İt Dalaşı", "Kamikaze ", "Otonom İniş"]
        self.options = tkinter.StringVar(master=self.mainWindow)
        self.options.set("Select an operation")
        self.operations = tkinter.OptionMenu(self.mainWindow,self.options,*options_list)
        self.operations.config(width=15,height=3,background="lightblue",border=5)
        self.operations.grid(row=2,column=4,sticky='sw')
        
        #####################
        
        
        self.time_label = tkinter.Label(self.mainWindow)
        self.time_label.config(text="Sunucu Saati:",font=("Arial",22))
        self.time_label.grid(row=0,column = 2)
        self._time()
        self.telemetry_label = tkinter.Label(self.mainWindow,wraplength=250)
        self.telemetry_label.grid(row = 1,column=2)
        self._telemetry_label()
        # Frame for the time spinners
        timeFrame = tkinter.LabelFrame(self.mainWindow, text="Time")
        timeFrame.grid(row=3, column=0, sticky='new')
        ##Camera
        self.camera = tkinter.LabelFrame(self.mainWindow)
        self.camera.config(width=30,height=20)
        self.camera.grid(row =1,column= 4 )
        #self._getcamera()
        # Buttons
        okButton = tkinter.Button(self.mainWindow, text="OK")
        okButton.config(width=15,height= 3,background='darkgreen',border=10)
        cancelButton = tkinter.Button(self.mainWindow, text="Cancel", command=self.mainWindow.destroy)
        cancelButton.config(width=15,height= 3,background='red',border=10)
        okButton.grid(row=4, column=4, sticky='e')
        cancelButton.grid(row=4, column=5, sticky='w')
        self.submit_button = tkinter.Button(self.mainWindow,text='Komut Yolla',command=self._getoptions)
        self.submit_button.config(width=16,height=3,background='brown',border=5)
        self.submit_button.grid(row =3 , column= 4 ,sticky='sw')
        global team_number
        self.map_widget.after(200, self.update,team_number)
    

    def run(self):
        self.mainWindow.mainloop()

    def update(self,team_number):
        geodesic = Geod(ellps='WGS84')
        self.__get_data()
        global our_telemetry
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
            for a in enemy:
                if a["takim_numarasi"] == team_number:
                    our_telemetry = a
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

class Categorize():
    def __init__(self,team_number:int,starting_point:list):
        self.localization = Localization(starting_point =starting_point)
        self.camera = Camera()
        self.camerathread = threading.Thread(target=self.camera.detect)
        self.camerathread.start()
        self.team_number = team_number
        self.count = 0
        self.corresponding_enemy_list = []
        self.route = []
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

            pred_lat_1sec,pred_lon_1sec,pred_time_1sec=self.polynomial_pred(lat,lon,ele,6)
            enlem_list.append(pred_lat_1sec)
            boylam_list.append(pred_lon_1sec)
            time.append(pred_time_1sec)
            prediction_list.append({"enemy_id":enemy[-1]["enemy_id"],"pred_lat_1sec":pred_lat_1sec,"pred_lon_1sec":pred_lon_1sec,"pred_time_1sec":pred_time_1sec})

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
            plt.close('all') """
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
                    in_range_list[0]=[enemy[-1]["turn_direction_for_us"],escape_angle,alt_command,speed,enemy[-1]["enemy_id"]]
                    in_range_count = in_range_count + 1
                elif characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("priority2") == True and characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("is_dangerous")== True:
                    speed = 75 
                    if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("avoid_immediate") == True:
                        speed = 100
                    escape_angle= 90 + enemy[-1]["Qrotate"]
                    in_range_count = in_range_count + 1
                    in_range_list[1]=[enemy[-1]["turn_direction_for_enemy"],escape_angle,alt_command,speed,enemy[-1]["enemy_id"]]
                elif characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("priority3") == True and characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("is_dangerous")== True:
                    speed = 75
                    if characteristics_list.get("enemy_id{}".format(enemy[-1]["enemy_id"])).get("avoid_immediate") == True:
                        speed = 100
                    escape_angle= 90 + enemy[-1]["Qrotate"]
                    in_range_count = in_range_count + 1
                    in_range_list[2]=[enemy[-1]["turn_direction_for_enemy"],escape_angle,alt_command,speed,enemy[-1]["enemy_id"]]
                else : 
                    continue
        if in_range_count == 1:
            for i in in_range_list:
                if i != 0:
                    print("Turn {} with {} , {} and accelerate at %{} speed \n".format(i[0],i[1],i[3],i[4]))
        elif in_range_count == 2:
            print("Slow down to the %10 speed and turn right")
        elif in_range_count == 3:
            print("Slow down to the %10 speed and turn right and dive")
        else:
            print("Continue Mission")
        self.enemy_list.clear()
        self.characteristic_list = characteristics_list
        return in_range_list

    def create_route(self,prediction_list):
        collision_flag = False
        point_list = []
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
                        else:
                            collision_flag = False
                if enemy[-1]['where_is_enemy'] == 'front':
                    direction = enemy[-1]['turn_direction_for_us']
                    angle = enemy[-1]['Qtrack']
                    #Açıya göre yol parametresi çizimi yap
                for prediction in prediction_list:
                    if prediction["enemy_id"] == enemy[-1]["enemy_id"]:
                        if collision_flag == True:
                            point = self.collision_goto([enemy[-1]["Enlem"],enemy[-1]["Boylam"]],enemy[-1]["lat_change"],enemy[-1]["lon_change"],prediction)
                        else:
                            point = [prediction["pred_lat_1sec"],prediction["pred_lon_1sec"]]
                        point_list.append(point)
                return point_list
                #Yakındaki düşmanlardan birine tahmin edilmiş koordinat noktasına göre yaklaş eğer yol üstünde çarpışma varsa yol değiştir.
    def collision_goto(self,location,lat_change,lon_change):
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
    def create_decision(self,prediction_list):
        #Görüntü İşlemeden gelecek sonuçları buraya ilet
        in_range_list = self.create_escape()
        route_list = self.create_route(prediction_list)


        return True
    def goto(self,location):
        pass
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
        return behaviour_dict
     
    def flight_controller(self,incoming_data:list):
        global previous_location_list
        global k
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
            self.create_decision(prediction_list)
        return [self.corresponding_enemy_list]    



class Localization():
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
        self.start_x ,self.start_y = self.get_x_y_coordinates(starting_point[0],starting_point[1])
        self.start_x = self.map_mid_x - self.start_x
        self.start_y = (self.map_mid_y - self.start_y) * -1
        self.estimation_initialized = False
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

def localization():
    telemetry_list = telemetry_data.get_data()
    for i in range(7):
        behaivour_dict=drive.flight_controller(incoming_data=telemetry_list[i])
        
        time.sleep(0.987)
    
if __name__ == "__main__":
    start = datetime.now()
    startpoint = [39.854818,32.781299,100]
    drive = Categorize(team_number=team_number,starting_point=startpoint)
    #window = Window()
    thread = threading.Thread(target=localization)
    thread.start()
    #window.run()
    print(datetime.now() - start)
    
        


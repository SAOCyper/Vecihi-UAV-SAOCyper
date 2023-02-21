from datetime import datetime
import cv2
import math,time
from numpy import mean
import numpy as np
from numpy.polynomial import Polynomial as P
import warnings
#Camera Global Paremeters
lock_on = False
lock_on_started = False
lock_on_finished = False
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
cap = cv2.VideoCapture(0)
warnings.simplefilter('ignore', np.RankWarning)
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
        #global telemetry_packager 
        self.trained_face_data = cv2.CascadeClassifier(r'C:\CYCLOP\GLADOS\haarcascade_frontalface_default.xml')
        
        self.telemetry_packager = TelemetryCreate()
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
        print("ok")
        global lock_on , lock_on_started , lock_on_finished ,  cap
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
        while(cap.isOpened()):
                # Capture frame-by-frame
                t0 = time.time()
                if len(current_bbox_frame) > 1000:
                    current_bbox_frame.clear()
                global frame , start , kilitlenme_sayısı ,kilitlenme ,diff_info ,hedef_merkez_x,hedef_merkez_y,başlangıç_zamanı,bitiş_zamanı
                ret, frame = cap.read()
                # if frame is read correctly ret is True
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break
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
                        if len(current_bbox_frame) > 1:
                            movement_direction_x = current_bbox_frame[-1][0] - prev_bbox_frame[-1][0]
                        if movement_direction_x > 0:
                            direction="Right"
                        else:
                            direction="Left"
                        current_bbox_frame.append((framemid_x,framemid_y))
                        if frame_count <= 2:
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
                                    tracking_objects.pop(object_id)
                        """ for object_id , pt in tracking_objects.items():
                            cv2.putText(frame , str(object_id),(pt[0],pt[1]-7),0,1,(0,0,255),1) """
                        if point_count < 20:
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
                                print(y_p(mid_desired_x))
                                cv2.circle(frame,(x,y_prediction),2,(255,0,255),cv2.FILLED)
                                cv2.circle(frame,(mid_desired_x,predicted_y),7,(0,0,255),cv2.FILLED)
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
                                    lock_on_started = self.telemetry_packager.Kilitlenme_başlangıç()
                                    #lock_on_started = True
                                    start = datetime.now()
                                    başlangıç_zamanı = Camera._GPS_Saati()
                                diff = (datetime.now() - start).seconds
                                if success == True:
                                        success = False
                                        Camera.Success = False
                                if diff == 2:
                                    kilitlenme =False
                                    
                                Camera.Time = diff 
                                if diff == 4:
                                    lock_on_finished = self.telemetry_packager.Kilitlenme_bitiş()
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
                else : 
                    start = 0
                    kilitlenme = False
                # Display the resulting frame
                t = time.time()-t0
                self.fpsArray.append(1/t)
                averageFPS = mean(self.fpsArray)
                cv2.putText(frame,'FPS:' + str(averageFPS)[:4], (510,20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 1, cv2.LINE_AA)
                #self.recorder.write(frame)
                del self.fpsArray[:-180]
                """ cv2.imshow('preview',frame) """
                key = cv2.waitKey(20)
                if key & 0xFF == ord('q'):
                    for i in range(3):
                        print("....CLOSING CAMERA in {} second ....".format(3-i))
                        
                        time.sleep(1)
                    break
        # When everything done, release the capture
        cap.release()
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

camera = Camera()
camera.detect()
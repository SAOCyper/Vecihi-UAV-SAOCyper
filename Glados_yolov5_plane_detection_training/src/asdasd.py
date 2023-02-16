import math
import cv2,time
from datetime import datetime
from numpy import mean
fpsArray = []
averageFPS = 0
frame = 0
temp_m1 = 0.1
temp_m2 = 0.1
start = 0
#Camera Global Paremeters
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
def get_angle(pointlist:list):
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
def detect():
        while True:
                frame = cv2.imread(r'C:\uav_168.jpg')  
                """ frame.resize((640,480,3)) """
                # Capture frame-by-frame
                t0 = time.time()
                x = 713
                y = 413
                w = 939 - 713
                h =  588 - 413
                global  start , kilitlenme_sayısı ,kilitlenme ,diff_info ,hedef_merkez_x,hedef_merkez_y,başlangıç_zamanı,bitiş_zamanı
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
                cv2.rectangle(frame,(hitbox_left,hitbox_up),(hitbox_right,hitbox_down),color=(255, 17, 255),thickness=3)
                cv2.putText(frame,text="Hit Zone",org=(hitbox_left,hitbox_down+35),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1,color=(255, 17, 255))
                success = False
                end_cord_x = x + w
                end_cord_y = y + h
                framemid_x = int((end_cord_x + x)/2)
                framemid_y = int((end_cord_y + y)/2)
                dikey = ((end_cord_y - y)/rows)*100
                yatay = ((end_cord_x - x)/cols)*100
                point_list = [(hitbox_midpointx,hitbox_midpointy),(framemid_x,framemid_y),(hitbox_midpointx-1,0)]
                angle ,direction= get_angle(point_list)
                Angle = angle
                Direction = direction
                cv2.line(frame,(hitbox_midpointx,hitbox_midpointy),(framemid_x,framemid_y),color = (255,255,255),thickness=2)
                #cv2.rectangle(frame, (x, y), (end_cord_x, end_cord_y), color=(0, 0, 255), thickness=2)
                cv2.putText(frame,text="Dikey = %{:.2f}".format(dikey),org=(end_cord_x+10, y+15),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(22,159,230),thickness=2,lineType=cv2.LINE_AA)
                cv2.putText(frame,text="Yatay = %{:.2f}".format(yatay),org=(end_cord_x-70, y-15),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5,color=(22,159,2230),thickness=2,lineType=cv2.LINE_AA)
                if (x > hitbox_left and end_cord_x < hitbox_right) and (y > hitbox_up and end_cord_y < hitbox_down):
                    if ( yatay > 5) and ( dikey > 5):
                        if start == 0:
                            start = datetime.now()
                        diff = (datetime.now() - start).seconds
                        if diff == 1 :
                            Success = False
                        if diff == 2:
                            kilitlenme =False
                            if success == True:
                                success = False
                        Time = diff 
                        if diff == 4:
                            hedef_merkez_x = int((x+x+w)/2)
                            hedef_merkez_y = int((y+y+h)/2)
                            print(hedef_merkez_x,hedef_merkez_y)
                            kilitlenme_sayısı = kilitlenme_sayısı +1 
                            success = True
                            Success = success
                            kilitlenme = True
                            start = 0
                            print("Kilitlenme Sayısı:{}".format(kilitlenme_sayısı))
                        if kilitlenme == True :
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

                cv2.putText(frame,'FPS:' + str(125), (510,20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 1, cv2.LINE_AA)
                cv2.imshow('frame',frame)
                if cv2.waitKey(20) & 0xFF == ord('q'):
                    for i in range(3):
                        print("....CLOSING CAMERA in {} second ....".format(3-i))
                        time.sleep(1)
                    break
                            # When everything done, release the capture

        cv2.destroyAllWindows()

detect()
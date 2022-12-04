import customtkinter
import threading,folium,os
import time
from datetime import datetime
from selenium import webdriver
from PIL import ImageTk, Image

def Window():
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")
    root = customtkinter.CTk()
    root.geometry("1400x680")
    image1 = Image.open(r"C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\output.png")
    image1 = image1.resize((900, 650), Image.ANTIALIAS)
    test = ImageTk.PhotoImage(image1)
    frame = customtkinter.CTkFrame(master = root)
    frame.pack(pady=20,padx=60,fill="both",expand=True)
    label = customtkinter.CTkLabel(master=frame,text="2D Space",text_font=("Roboto",24))
    label.pack(pady=12,padx=10)
    label1 = customtkinter.CTkLabel(master=frame,image=test)
    label1.pack(pady=12,padx=10)
    
    root.mainloop()

class Map():
    def __init__(self):
        z1 = (39.860948, 32.770010)
        z2 = (39.864205,32.788550)
        z3 = (39.844797, 32.781285)
        z4 = (39.853096, 32.806683)
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
        self.our_map = folium.Map(location=[39.856398, 32.780181],zoom_start=14)
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
    def map_generate(self):
        map_name = "output.html"
        self.our_map.save("output.html")
        map_url = 'file://{}/{}'.format(os.getcwd(),map_name)
        driver = webdriver.Chrome(executable_path=r"C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\src\chromedriver.exe")
        driver.get(map_url)
        time.sleep(1)
        driver.save_screenshot('output.png')
        driver.quit
start = datetime.now()
map = Map()
thread = threading.Thread(target=map.map_generate,args=())
thread1 = threading.Thread(target=Window,args=())
thread.start()
thread1.start()
print(datetime.now() - start)
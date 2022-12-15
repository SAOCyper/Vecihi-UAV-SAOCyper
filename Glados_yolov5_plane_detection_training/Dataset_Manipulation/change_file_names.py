from pathlib import Path
import os
from PIL import Image
photo_number = 1500 #Buraları klasördeki son dosyaya göre değiştir
txt_number = 1500 #Buraları klasördeki son dosyaya göre değiştir
for path in Path(r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation\alljpg').rglob('*.jpg'):
    replacement ="uav_{}".format(photo_number)
    tmp_path_origin_jpg = path
    photo_number = photo_number + 1
    file_name_jpg = path.parts[8]
    file_name_jpg =file_name_jpg.replace(file_name_jpg[:-4],replacement)
    path = list(path.parts)
    path[8] = file_name_jpg
    tmp_path_jpg = 'C:'
    a = 0
    for i in path:
        if a != 0:
            tmp_path_jpg = tmp_path_jpg + "\{}".format(i)
        a = a +1
    path = tuple(path)
    os.rename(tmp_path_origin_jpg,tmp_path_jpg) 


for path in Path(r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation\alltxt').rglob('*.txt'):
    replacement ="uav_{}".format(txt_number)
    tmp_path_origin = path
    txt_number = txt_number + 1
    file_name = path.parts[8]
    file_name =file_name.replace(file_name[:-4],replacement)
    path = list(path.parts)
    path[8] = file_name
    tmp_path = 'C:'
    a = 0
    for i in path:
        if a != 0:
            tmp_path = tmp_path + "\{}".format(i)
        a = a +1
    path = tuple(path)
    os.rename(tmp_path_origin,tmp_path)

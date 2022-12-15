from PIL import Image
from pathlib import Path
import os
process = input()
dir_number = 1
if process == "Convert":
    for path in Path(r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation').rglob('*.png'):
        im1 = Image.open(path)
        print(path.name)
        replacement ="jpg"
        print(path)

        file_name = path.parts[7]

        file_name =file_name.replace(file_name[-3:],replacement)
        path = list(path.parts)
        path[7] = file_name
        tmp_path = os.path.join(path[0],path[1])
        path.pop(0)
        path.pop(0)
        for i in path:
            tmp_path = tmp_path + "\{}".format(i)
            #tmp_path = os.path.join(tmp_path,"\{}".format(i))

        im1.save(tmp_path)
elif process == "Delete":
    for path in Path(r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation').rglob('*.png'): 
        os.remove(path)

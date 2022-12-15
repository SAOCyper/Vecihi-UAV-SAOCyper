from pathlib import Path
import os
from PIL import Image
from sklearn.model_selection import train_test_split
import shutil
images = [os.path.join(r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation\alljpg', x) for x in os.listdir(r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation\alljpg') if x[-3:] == "jpg"]
labels = [os.path.join(r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation\alltxt', x) for x in os.listdir(r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation\alltxt') if x[-3:] == "txt"]
images.sort()
labels.sort()

# Split the dataset into train-valid-test splits 
train_images, val_images, train_labels, val_labels = train_test_split(images, labels, test_size = 0.2, random_state = 1)
val_images, test_images, val_labels, test_labels = train_test_split(val_images, val_labels, test_size = 0.5, random_state = 1)

#Utility function to move images 
def move_files_to_folder(list_of_files, destination_folder):
    for f in list_of_files:
        try:
            shutil.move(f, destination_folder)
        except:
            print(f)
            assert False


# Move the splits into their folders
move_files_to_folder(train_images, r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation\datasets\images\train')
move_files_to_folder(val_images, r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation\datasets\images\val')
move_files_to_folder(test_images, r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation\datasets\images\test')
move_files_to_folder(train_labels, r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation\datasets\labels\train')
move_files_to_folder(val_labels, r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation\datasets\labels\val')
move_files_to_folder(test_labels, r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\Dataset_Manipulation\datasets\labels\test')
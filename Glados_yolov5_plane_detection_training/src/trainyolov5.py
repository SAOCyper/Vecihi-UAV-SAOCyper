import torch
from IPython.display import Image  # for displaying images
import os 
import random
import shutil
from sklearn.model_selection import train_test_split
import xml.etree.ElementTree as ET
from xml.dom import minidom
from tqdm import tqdm
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
from Glados_yolov5_plane_detection_training.VOC_Parser import VOC_Parser

# Read images and labels
images = [os.path.join('dataset/images', x) for x in os.listdir('dataset/images') if x[-3:] == "jpg"]
labels = [os.path.join('dataset/labels', x) for x in os.listdir('dataset/labels') if x[-3:] == "txt"]

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
move_files_to_folder(train_images, 'dataset/images/train')
move_files_to_folder(val_images, 'dataset/images/val/')
move_files_to_folder(test_images, 'dataset/images/test/')
move_files_to_folder(train_labels, 'dataset/labels/train/')
move_files_to_folder(val_labels, 'dataset/labels/val/')
move_files_to_folder(test_labels, 'dataset/labels/test/')
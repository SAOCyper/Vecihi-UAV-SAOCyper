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

class VOC_Parser:
    def __init__(self):
        # Dictionary that maps class names to IDs
        self.class_name_to_id_mapping = {"airplane": 0}

    # Function to get the data from XML Annotation
    def extract_info_from_xml(self,xml_file):
        root = ET.parse(xml_file).getroot()
        
        # Initialise the info dict 
        self.info_dict = {}
        self.info_dict['bboxes'] = []

        # Parse the XML Tree
        for elem in root:
            # Get the file name 
            if elem.tag == "filename":
                self.info_dict['filename'] = elem.text
                
            # Get the image size
            elif elem.tag == "size":
                image_size = []
                for subelem in elem:
                    image_size.append(int(subelem.text))
                
                self.info_dict['image_size'] = tuple(image_size)
            
            # Get details of the bounding box 
            elif elem.tag == "object":
                bbox = {}
                for subelem in elem:
                    if subelem.tag == "name":
                        bbox["class"] = subelem.text
                        
                    elif subelem.tag == "bndbox":
                        for subsubelem in subelem:
                            bbox[subsubelem.tag] = int(subsubelem.text)            
                self.info_dict['bboxes'].append(bbox)
        
        return self.info_dict


    # Convert the info dict to the required yolo format and write it to disk
    def convert_to_yolov5(self):
        print_buffer = []
        
        # For each bounding box
        for b in self.info_dict["bboxes"]:
            try:
                class_id = self.class_name_to_id_mapping[b["class"]]
            except KeyError:
                print("Invalid Class. Must be one from ", self.class_name_to_id_mapping.keys())
            
            # Transform the bbox co-ordinates as per the format required by YOLO v5
            b_center_x = (b["xmin"] + b["xmax"]) / 2 
            b_center_y = (b["ymin"] + b["ymax"]) / 2
            b_width    = (b["xmax"] - b["xmin"])
            b_height   = (b["ymax"] - b["ymin"])
            
            # Normalise the co-ordinates by the dimensions of the image
            image_w, image_h, image_c = self.info_dict["image_size"]  
            b_center_x /= image_w 
            b_center_y /= image_h 
            b_width    /= image_w 
            b_height   /= image_h 
            
            #Write the bbox details to the file 
            print_buffer.append("{} {:.3f} {:.3f} {:.3f} {:.3f}".format(class_id, b_center_x, b_center_y, b_width, b_height))
            
        # Name of the file which we have to save 
        save_file_name = os.path.join("dataset_pascalvoc\\test", self.info_dict["filename"].replace("jpg", "txt"))
        
        # Save the annotation to disk
        print("\n".join(print_buffer), file= open(save_file_name, "w"))

        
    def get_annotations(self): 
        # Get the dataset_pascalvoc
        self.dataset_pascalvoc = [os.path.join('dataset_pascalvoc\\test', x) for x in os.listdir('dataset_pascalvoc\\test') if x[-3:] == "xml"]
        self.dataset_pascalvoc.sort()
        

        # Convert and save the dataset_pascalvoc
        for ann in tqdm(self.dataset_pascalvoc):
            info_dict = VOC_Parser.extract_info_from_xml(ann)
            VOC_Parser.convert_to_yolov5(info_dict)
        self.dataset_pascalvoc = [os.path.join('dataset_pascalvoc', x) for x in os.listdir('dataset_pascalvoc') if x[-3:] == "txt"]
        self.class_id_to_name_mapping = dict(zip(self.class_name_to_id_mapping.values(), self.class_name_to_id_mapping.keys()))
        return self.dataset_pascalvoc
        
        
    def plot_bounding_box(self,image, annotation_list):
        dataset_pascalvoc = np.array(annotation_list)
        w, h = image.size
        
        plotted_image = ImageDraw.Draw(image)

        transformed_dataset_pascalvoc = np.copy(dataset_pascalvoc)
        transformed_dataset_pascalvoc[:,[1,3]] = dataset_pascalvoc[:,[1,3]] * w
        transformed_dataset_pascalvoc[:,[2,4]] = dataset_pascalvoc[:,[2,4]] * h 
        
        transformed_dataset_pascalvoc[:,1] = transformed_dataset_pascalvoc[:,1] - (transformed_dataset_pascalvoc[:,3] / 2)
        transformed_dataset_pascalvoc[:,2] = transformed_dataset_pascalvoc[:,2] - (transformed_dataset_pascalvoc[:,4] / 2)
        transformed_dataset_pascalvoc[:,3] = transformed_dataset_pascalvoc[:,1] + transformed_dataset_pascalvoc[:,3]
        transformed_dataset_pascalvoc[:,4] = transformed_dataset_pascalvoc[:,2] + transformed_dataset_pascalvoc[:,4]
        
        for ann in transformed_dataset_pascalvoc:
            obj_cls, x0, y0, x1, y1 = ann
            plotted_image.rectangle(((x0,y0), (x1,y1)))
            
            plotted_image.text((x0, y0 - 10), self.class_id_to_name_mapping[(int(obj_cls))])
        
        plt.imshow(np.array(image))
        plt.show()
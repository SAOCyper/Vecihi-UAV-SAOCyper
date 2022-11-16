```
Author : Mert Ünübol
Date : 25.10.2022
```
**STEPS TO FOLLOW**
===============
 1. **Before proceeding create a virtual environment with:**  
    ```
        python -m venv yourenvironmentname
    ```
 2. **Then activate your environment with:**  
    ```
        yourenvironmentname\Scripts\activate 
    ```
 3. **After that install the dependencies with:** 
    ```
        pip install -r requirements.txt
    ```
 4. **After installing all dependencies clone yolov5 from github with and create your dataset.yaml file follow the steps:**
    ```
        git clone https://github.com/ultralytics/yolov5.git
        cd yolov5
    ```
    1. **create a new file named as dataset.yaml and copy paste following lines:**
        ```
            path: ../Glados_yolov5_plane_detection_training/plane_dataset  # dataset root dir
            train: images/train  # train images (relative to 'path') 128 images
            val: images/val  # val images (relative to 'path') 128 images
            test:  images/test # test images (optional)
            # Classes 
            names:
            0: plane
        ```
  

## **YOLOV5 training parameters**
    parameters:
            --data dataset.yaml It has path locations of our dataset images and labels 
            --epochs    is number of turns that our train functions training time.Usually 1000 would be good but training would too long
            --img       is the image size -
            --batch     Think of a batch as a for-loop iterating over one or more samples and making predictions. At the end of the batch, the predictions are  
                        compared to the expected output variables and an error is calculated. From this error, the update algorithm is used to improve the model
            --nosave and --cache    will speed up the training process
        
### **Use below command to train yolov5 model**:
    
    python train.py --img 640 --batch 16 --epochs 100 --data dataset.yaml --weights yolov5s.pt --nosave --cache 
    
**SocketServer Usage**
==================
1. app-server.py
    - Connect to the server with the ip of your computer's  and with port = 65432
    - ```
        python app-server.py 192.168.1.102 65432 
      ```
2. app-client.py
    - **Available Requests**
        1. GET
            1. get /sunucusaati
            2. get /qr_koordinati
            3. get morpheus
            4. get ring
            5. get \U0001f436
        2. POST
            1. post /api/telemetri_gonder
            2. post /api/kilitlenme_bilgisi
            3. post /api/giris
            4. post /api/kamikaze_bilgisi
    -   **Example**
        ```
            python app-client.py 192.168.1.102 65432 post /kamikaze_bilgisi
        ```

**PlaneController**
==================
## **Functions**
1. Create list
    It creates a list with a different telemetry datas from different planes.After that it creates an small area as a map for converting our latitude and longitude values to x and y coordinates.Reason for that map is as we live in a globe latitude and longitudes are arc values hence we can't convert them to coordinate values very well without using some sort of techniques.
    This way is optimal way for me .After creating a map and obtaining our center point we can calculate x and y values of every plane and we can place them in our coordinate system.This way we can get => Q1,Q2,Q3,Q4.With comparing our own plane location change we can find our direction vector.
    After some math equations we can find the distance difference between our plane and every plane.We can also calculate horizontal angles in order for our plane to automatically chase its prey.After getting all these informations.By comparing results from previous telemetry datas we can categorize other planes with respect to danger.If they are chasing us or not.We can use this catalog for escaping algorithm later.
    
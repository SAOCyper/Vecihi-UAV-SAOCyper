```
Author : Mert Ünübol
Date : 25.10.2022
```
STEPS TO FOLLOW
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
    
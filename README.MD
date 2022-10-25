Author : Mert Ünübol
Date : 25.10.2022
Before proceeding create a virtual environment with : python -m venv yourenvironmentname
Then activate your environment with : yourenvironmentname\Scripts\activate 
After that install the dependencies with : pip install -r requirements.txt

Use below command to train yolov5 model:
    parameters:
        --data dataset.yaml It has path locations of our dataset images and labels 
        --epochs    is number of turns that our train functions training time.Usually 1000 would be good but training would too long
        --img       is the image size -
        --batch     Think of a batch as a for-loop iterating over one or more samples and making predictions. At the end of the batch, the predictions are  
                    compared to the expected output variables and an error is calculated. From this error, the update algorithm is used to improve the model
        --nosave and --cache    will speed up the training process
python train.py --img 640 --batch 16 --epochs 100 --data dataset.yaml --weights yolov5s.pt --nosave --cache 
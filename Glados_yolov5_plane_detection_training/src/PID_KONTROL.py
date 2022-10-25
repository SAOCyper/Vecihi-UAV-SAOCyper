import numpy as np
import random
def box_cleaner(bboxes):
    bboxes=[np.array([1,2,3,4,"pot"]),np.array([3,4,5,6,"person"]),np.array([6,7,1,9,"person"]),np.array([123,435,231,652,"person"]),np.array([178,257,265,32,"person"]),np.array([65,234,57,546,"person"])]
    box_storage = []
    i=0
    for box in bboxes:

        box_points=[0,1]
        if box[4]=="person":
            p1=box[0]
            p4=box[0]+box[2]
            box_points[0]=p1
            box_points[1]=p4
            box_storage.append(box_points)

        
    removable_items_index=[]
    for i in range(len(box_storage)):
        for j in range(i + 1, len(box_storage)):
            if box_storage[i][0] > box_storage[j][0] and box_storage[i][1] < box_storage[j][1] :
                removable_items_index.append(i+1)
                print(f"Number {i} box is inside of number {i+1}")
            elif box_storage[i][0] < box_storage[j][0] and box_storage[i][1] > box_storage[j][1] :  
                removable_items_index.append(i)  
                print(f"Number {i} box is outside of number {i+1}")
            else:
                print(f"Number {i} box irrevelant with box number {i+1}")
    for i in range(len(removable_items_index)):
        del bboxes[removable_items_index[i]]




def pid_control(setpoint,currentpoint,frame_rows,frame_cols):
    turn_degree = np.arange(0, 72)
    i=0
    angle=0
    multiples_9 = [n for n in range(1, 298) if n % 9 == 0]
    for item in multiples_9:
        turn_degree[i]=5*i
        
        i=i+1
    x_difference = abs(setpoint[0]-currentpoint[0])
    y_difference = abs(setpoint[1]-currentpoint[1])
    width=frame_rows-0
    height=frame_cols-0
    error_rate_x=x_difference/width *100
    error_rate_y=y_difference/height *100
    if error_rate_x < 1 :
        angle=None
        return angle
    
    for k in range(len(multiples_9)):
        for j in range(k + 1, len(multiples_9)):
            if error_rate_x<multiples_9[k]:
                angle=turn_degree[k+1]
                break
            elif error_rate_x>multiples_9[k] and error_rate_x < multiples_9[j]:
                angle=turn_degree[j+1]
                break
        if angle != 0:
            break
    return angle


def set_start_point():
    currentpoint=[0,1]
    currentpoint[0] = random.randint(0, 640)
    currentpoint[1] = random.randint(0, 480)
    return currentpoint
def pidtest():
    startpoint=set_start_point()
    rows=640
    cols=480
    setpoint=[320,240]
    counter=0
    prev_angle=None
    while True:
        angle=pid_control(setpoint=setpoint,currentpoint=startpoint,frame_rows=rows,frame_cols=cols)
        if angle is None:
            print(startpoint[0])
            break
        fark=angle / 5
        pixel_difference = fark*71

        
        if angle == prev_angle:
            counter = counter +1
            fark=angle / 5
            pixel_difference = fark*71
            if counter ==3:
                fark=angle/5
                pixel_difference=fark*51
            elif counter == 4:
                fark=angle/5
                pixel_difference=fark*31
            elif counter == 5:
                fark=angle/5
                pixel_difference=fark*11
            elif 12>counter>5:
                fark=angle/5
                pixel_difference=fark*2
        prev_angle=angle
        if startpoint[0] <320:
            startpoint[0]=startpoint[0]+pixel_difference
            continue
        elif startpoint[0] > 320 :
            startpoint[0]=startpoint[0]-pixel_difference
            continue

    
for i in range(100):
    pidtest()

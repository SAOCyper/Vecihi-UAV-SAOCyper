import glob
import cv2
import pandas as pd
import pathlib

def qr_kod():

    try:
            img = cv2.imread(r'C:\qr_sagust.jpeg')
            detect = cv2.QRCodeDetector()
            value, points, straight_qrcode = detect.detectAndDecode(img)
            return value
    except:
            return

print(qr_kod())
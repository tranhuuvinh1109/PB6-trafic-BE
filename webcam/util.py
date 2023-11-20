import cv2
import string
from skimage.filters import threshold_local
from skimage import measure
import numpy as np
import imutils
from PIL import Image

def convert_to_binary(license_plate_crop):
    # Chuyển ảnh sang ảnh xám
    gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)

    # Áp dụng adaptive thresholding
    T = threshold_local(gray, 15, offset=10, method="gaussian")
    thresh = (gray > T).astype("uint8") * 255

    # Chuyển pixel đen sang trắng và ngược lại
    thresh = cv2.bitwise_not(thresh)
    # thresh = imutils.resize(thresh, width=100)
    thresh = cv2.resize(thresh,(100,100),interpolation=cv2.INTER_LANCZOS4) #or INTER_CUBIC
    
    # blurred = cv2.GaussianBlur(thresh, (5, 5), 0)
    # sharpened = cv2.addWeighted(thresh, 2.0, blurred, -0.5, 0)
    # resized = cv2.resize(sharpened, (150, 150))

    return thresh


def get_car(license_plate, vehicle_track_ids):
    x1, y1, x2, y2, score, class_id = license_plate

    foundIt = False
    for j in range(len(vehicle_track_ids)):
        xcar1, ycar1, xcar2, ycar2, car_id = vehicle_track_ids[j]

        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            car_indx = j
            foundIt = True
            break

    if foundIt:
        return vehicle_track_ids[car_indx]

    return -1, -1, -1, -1, -1



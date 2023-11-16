from datetime import datetime
from ultralytics import YOLO
import cv2
import numpy as np
from sort.sort import *
from .util import *
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

results = {}
mot_tracker = Sort()
new_width = 1400
new_height = 1000
vehicles = [2, 3, 5, 7]
frame_nmr = -1
ret = True
frame_skip = 1  # Số frame bạn muốn bỏ qua giữa các lần xử lý   
# Danh sách biển số xe đã xử lý
processed_license_plates = []
saved_images = {}
MODEL_DIR = os.path.join(BASE_DIR, 'assets/models/yolov8n.pt')
LINCEMSE_MODEL_DIR = os.path.join(BASE_DIR,'assets/models/best.pt')
VIDEO_DIR = os.path.join(BASE_DIR, 'assets/videos/sample7.mp4')
MEDIA_DIR = os.path.join(BASE_DIR, 'pbl_traffic_be/media')
class_vehicle = 0


class Detech:
    def DetechLicensePlate():
        global ret
        ret = True
        global frame_nmr  # Declare frame_nmr as a global variable
        frame_nmr = -1 
        coco_model = YOLO(MODEL_DIR)
        license_plate_detector = YOLO(LINCEMSE_MODEL_DIR)

        cap = cv2.VideoCapture(VIDEO_DIR)

        formatted_datetime = datetime.now().strftime("%Y_%m_%d")
        PRESENT_DIR = os.path.join(MEDIA_DIR, 'day_'+formatted_datetime)
        SAVE_MEDIA_DIR = ''
        SAVE_BIARY_DIR = ''
        
        if not os.path.exists(PRESENT_DIR):
            os.makedirs(PRESENT_DIR)

        SAVE_MEDIA_DIR = os.path.join(PRESENT_DIR, 'result')
        SAVE_BIARY_DIR = os.path.join(PRESENT_DIR, 'binary')
        
        if not os.path.exists(SAVE_MEDIA_DIR):
            os.makedirs(SAVE_MEDIA_DIR)
            os.makedirs(SAVE_BIARY_DIR)
        
        
        while ret:
            frame_nmr += 1
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (new_width, new_height))
                results[frame_nmr] = {}
                if frame_nmr % frame_skip == 0:  # Bỏ qua frame không cần xử lý
                    detections = coco_model(frame, classes=[2, 3, 5, 7])[0]
                    detections_ = []
                    for detection in detections.boxes.data.tolist():
                        x1, y1, x2, y2, score, class_id = detection
                        if int(class_id) in vehicles:
                            class_vehicle = int(class_id)
                            print('line 66: ', int(class_id), class_vehicle)
                            detections_.append([x1, y1, x2, y2, score])
                    # Vẽ bounding boxes xung quanh các đối tượng đã phát hiện
                    for box in detections_:
                        x1, y1, x2, y2, _ = box
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                cv2.imshow('Detected Video', frame)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

                if frame_nmr % frame_skip == 0 and detections_:
                    track_ids = mot_tracker.update(np.asarray(detections_))
                    if frame_nmr % frame_skip == 0:
                        license_plates = license_plate_detector(frame)[0]
                        for license_plate in license_plates.boxes.data.tolist():
                            x1, y1, x2, y2, score, class_id = license_plate
                            print('===line 84 :',class_vehicle)

                            if license_plate not in processed_license_plates:
                                xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)
                                xcar1 = int(xcar1)
                                ycar1 = int(ycar1)
                                xcar2 = int(xcar2)
                                ycar2 = int(ycar2)
                                if xcar1 != -1 and ycar1 != -1 and xcar2 != -1 and ycar2 != -1:
                                    if car_id not in saved_images:
                                        frame_copy = frame.copy()
                                        cv2.rectangle(frame_copy, (xcar1, ycar1), (xcar2, ycar2), (0, 255, 0), 2)
                                        save_datetime = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
                                        output_path = os.path.join(SAVE_MEDIA_DIR, f"day_{save_datetime}-{car_id}-{class_vehicle}.png") # lưu id vehicles ở đây
                                        cv2.imwrite(output_path, frame_copy)
                                        saved_images[car_id] = True
                                        license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
                                        license_plate_crop_binary = convert_to_binary(license_plate_crop)
                                        binary_output_path = os.path.join(SAVE_BIARY_DIR, f"day_{save_datetime}-{car_id}-{class_vehicle}.png")# lưu id vehicles ở đây
                                        cv2.imwrite(binary_output_path, license_plate_crop_binary)
                                        cv2.imshow("Binary Image", license_plate_crop_binary)
                                                        
        cap.release()
        cv2.destroyAllWindows()



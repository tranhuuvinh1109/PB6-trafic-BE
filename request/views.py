import cv2
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ultralytics import YOLO
from request.detech import Detech
from datetime import datetime
import os
import easyocr
from request.serializers import VehicleSerializer
from .models import Vehicle
import numpy as np
from sort.sort import *
from .util import *

from django.http import HttpResponse
from django.conf import settings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results = {}
mot_tracker = Sort()
new_width = 1400
new_height = 1000
vehicles = [2, 3, 5, 7]
frame_nmr = -1
ret = True
frame_skip = 1  # Số frame bạn muốn bỏ qua giữa các lần xử lý   
processed_license_plates = []
saved_images = {}
MODEL_DIR = os.path.join(BASE_DIR, 'assets/models/yolov8n.pt')
LINCEMSE_MODEL_DIR = os.path.join(BASE_DIR,'assets/models/best.pt')
VIDEO_DIR = os.path.join(BASE_DIR, 'assets/videos/sample7.mp4')
VIDEO_DIR_2 = os.path.join(BASE_DIR, 'assets/videos/night.mp4')
MEDIA_DIR = os.path.join(BASE_DIR, 'pbl_traffic_be/media')
class_vehicle = 0
stop_streaming = False


def create_vehicle(data):
    try:
        new_vehicle = Vehicle(
            location=data.get('location'),
            type=data.get('type'),
            license=data.get('license'),
            time=data.get('time'),
            image_origin=data.get('image_origin'),
            image_detect=data.get('image_detect'),
            confidence=data.get('confidence', 0.0),
            license_fixed=data.get('license_fixed'),
            file_name=data.get('file_name'),
            folder_name=data.get('folder_name')
        )
        new_vehicle.save()
        return 1
    
    except Exception as e:
        print(f"Error saving vehicle: {e}")
        return None


class RootAPI(APIView):
    def get(self, request):
        return JsonResponse({"message": "Hey this is my API running 🥳"})
class DetechAPI(APIView):
    def get(self, request):
        print('running...')
        Detech.DetechLicensePlate()
        return JsonResponse({"message": "Hey this is my API running 🥳"})
    
class StreamAPI(APIView):
    def get(self, request):
        print('running...')
        return render(request, 'index.html')
    
def remove_specific_characters(input_str):
    special_characters = [';', '/', '\\', '*', '(', ')', '&', '^', '%', '$', '!', ' ', '[', ']', '-', '.', "'", ',', '?', '+', '}', '{']
    result_str = ''.join(char for char in input_str if char not in special_characters)

    return result_str

def fix(input_str):
    input_str = remove_specific_characters(input_str)
    dict_char_to_int = {'O': '0',
                        'D': '0',
                        'Q': '0',
                        'I': '1',
                        'J': '3',
                        'A': '4',
                        'G': '6',
                        'S': '5',
                        'B': '8',
                        'T': '4',
                        'L': '4',
                        'Z': '2',
                        '#': '4',
                        'E': '6',
                        'H': '4'
                        }

    dict_int_to_char = {'0': 'O',
                        '1': 'I',
                        '3': 'J',
                        '4': 'A',
                        '6': 'G',
                        '5': 'S',
                        '8': 'B',
                        '9': 'B'}

    result_str = ''

    for i, char in enumerate(input_str):
        if i == 0 and char in dict_char_to_int:
            result_str += dict_char_to_int[char]
        elif i == 1 and char in dict_char_to_int:
            result_str += dict_char_to_int[char]
        elif i == 2 and char in dict_int_to_char:
            result_str += dict_int_to_char[char]
        elif i > 2 and char in dict_char_to_int:
            result_str += dict_char_to_int[char]
        else:
            result_str += char

    return result_str
class LicensePlateAPI(APIView):
    def get(self, request):
        reader = easyocr.Reader(['en'])
        MEDIA_DIR = os.path.join(BASE_DIR, 'pbl_traffic_be/media')
        all_files = os.listdir(MEDIA_DIR)
        data = []

        for day_folder in all_files:
            day_folder_path = os.path.join(MEDIA_DIR, day_folder)

            if os.path.isdir(day_folder_path):
                binary_folder_path = os.path.join(day_folder_path, 'binary')
                result_folder_path = os.path.join(day_folder_path, 'result')

                binary_files = os.listdir(binary_folder_path) if os.path.exists(binary_folder_path) else []

                binary_data = {
                    "binary": []
                }

                for file in binary_files:
                    file_path = os.path.join(binary_folder_path, file)
                    result = reader.readtext(file_path)

                    confidence = sum(item[2] for item in result) / len(result) if result else 0.0
                    text = [item[1] for item in result]
                    text_fixed = fix((" ".join(text)).upper())

                    binary_data["binary"].append({
                        "location": 'DaNang',
                        "type": (file.split('-')[3]).split('.')[0],
                        "license": " ".join(text).upper(),
                        "license_fixed": text_fixed,
                        "confidence": confidence,
                        "folder_name": day_folder,
                        "file_name": file,
                        "image_origin": file.split('-')[0] + '/' + 'result' + '/' + file,
                        "image_detect": file.split('-')[0] + '/' + 'binary' + '/' + file,
                        "time": file.split('-')[1].replace('_', ':') + ' ' + file.split('-')[0][4:].replace('_', '/'),
                    })
                    if not Vehicle.objects.filter(file_name=file).exists():
                        print('not existing')
                        data_create = {
                            "location": 'DaNang',
                            "type": (file.split('-')[3]).split('.')[0],
                            "license": " ".join(text).upper(),
                            "confidence": confidence,
                            "image_origin": file.split('-')[0] + '/' + 'result' + '/' + file,
                            "image_detect": file.split('-')[0] + '/' + 'binary' + '/' + file,
                            "time": file.split('-')[1].replace('_', ':') + ' ' + file.split('-')[0][4:].replace('_','/'),
                            "license_fixed": text_fixed,
                            "file_name": file,
                            "folder_name": day_folder,
                        }
                        create_vehicle(data_create)
                    else:
                        print('---exxisst---')

                result_files = os.listdir(result_folder_path) if os.path.exists(result_folder_path) else []

                day_data = {
                    "folder_name": day_folder,
                    "detech": {
                        "binary": binary_data["binary"],
                        "result": result_files
                    }
                }
                data.append(day_data)

        return JsonResponse({"message": "Hey, this is my API running 🥳", "data": data})

    
class ListFileAPI(APIView):
    def get(self, request):
        MEDIA_DIR = os.path.join(BASE_DIR, 'pbl_traffic_be/media')
        all_files = os.listdir(MEDIA_DIR)
        data = []

        for day_folder in all_files:
            day_folder_path = os.path.join(MEDIA_DIR, day_folder)

            if os.path.isdir(day_folder_path):
                binary_folder_path = os.path.join(day_folder_path, 'binary')
                result_folder_path = os.path.join(day_folder_path, 'result')

                binary_files = os.listdir(binary_folder_path) if os.path.exists(binary_folder_path) else []
                result_files = os.listdir(result_folder_path) if os.path.exists(result_folder_path) else []
                day_data = {
                    'folder': day_folder,
                    'binary': binary_files,
                    'result': result_files
                }
                # day_data = {
                #     day_folder: {
                #         'binary': binary_files,
                #         'result': result_files
                #     }
                # }
                data.append(day_data)

        return JsonResponse({"message": "Hey, this is my API running 🥳", "data": data})


class AllVehiclesAPI(APIView):
    def get(self, request, format=None):
        vehicles = Vehicle.objects.all()
        serializer = VehicleSerializer(vehicles, many=True)
        return JsonResponse({"message": "Hey, this is my API running 🥳", "data": serializer.data, "status": 200})
    
class UpdateVehicle(APIView):
    def put(self, request, vehicle_id):
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            serializer = VehicleSerializer(vehicle, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                message = "Vehicle information updated successfully."
                return Response({"message": message}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Vehicle.DoesNotExist:
            error_message = "Vehicle not found."
            return Response({"error": error_message}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            error_message = f"Error updating vehicle: {e}"
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class DeleteAllVehicles(APIView):
    def delete(self, request):
        try:
            print('Deleting all vehicles')
            Vehicle.objects.all().delete()
            message = "All vehicles have been deleted."
            return Response({"message": message}, status=status.HTTP_200_OK)
        except Exception as e:
            error_message = f"Error deleting vehicles: {e}"
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def clear_stream(request):
    global stop_streaming
    print('--------------------------CLEAR------------------')
    stop_streaming = True
    return JsonResponse({'message': 'Streaming stopped successfully.'})

def stream(address_id):
    global stop_streaming
    stop_streaming = False  
    print('RUNIINGGG>>>> ....')
    global ret
    ret = True
    global frame_nmr
    frame_nmr = -1 
    coco_model = YOLO(MODEL_DIR)
    license_plate_detector = YOLO(LINCEMSE_MODEL_DIR)
    formatted_datetime = datetime.now().strftime("%Y_%m_%d")
    PRESENT_DIR = os.path.join(MEDIA_DIR, 'day_'+formatted_datetime)
    SAVE_MEDIA_DIR = ''
    SAVE_BIARY_DIR = ''
    URL_VIDEO = ''
    if(address_id == 1):
        URL_VIDEO = VIDEO_DIR
    else:
        URL_VIDEO = VIDEO_DIR_2
        
    cap = cv2.VideoCapture(URL_VIDEO)
    if not os.path.exists(PRESENT_DIR):
            os.makedirs(PRESENT_DIR)
    SAVE_MEDIA_DIR = os.path.join(PRESENT_DIR, 'result')
    SAVE_BIARY_DIR = os.path.join(PRESENT_DIR, 'binary')
    
    if not os.path.exists(SAVE_MEDIA_DIR):
        os.makedirs(SAVE_MEDIA_DIR)
        os.makedirs(SAVE_BIARY_DIR)
    while cap.isOpened():
        frame_nmr
        ret, frame = cap.read()
        if ret:
            results[frame_nmr] = {}
            if frame_nmr % frame_skip == 0:  # Bỏ qua frame không cần xử lý
                detections = coco_model(frame, classes=[2, 3, 5, 7])[0]
                detections_ = []
                for detection in detections.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = detection
                    if int(class_id) in vehicles:
                        class_vehicle = int(class_id)
                        detections_.append([x1, y1, x2, y2, score])
                # Vẽ bounding boxes xung quanh các đối tượng đã phát hiện
                for box in detections_:
                    x1, y1, x2, y2, _ = box
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                    
            cv2.imwrite('demo.jpg', frame)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + open('demo.jpg', 'rb').read() + b'\r\n')
        
            if stop_streaming:
                break      

            if detections_:
                track_ids = mot_tracker.update(np.asarray(detections_))
                if frame_nmr % frame_skip == 0:
                    license_plates = license_plate_detector(frame)[0]
                    for license_plate in license_plates.boxes.data.tolist():
                        x1, y1, x2, y2, score, class_id = license_plate

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
                                    # cv2.imshow("Binary Image", license_plate_crop_binary)
                
def index1(request):
    return render(request, 'index1.html')

def index2(request):
    return render(request, 'index2.html')

def video_feed_tdt(request):
    return StreamingHttpResponse(stream(1), content_type="multipart/x-mixed-replace;boundary=frame")

def video_feed_dbp(request):
    return StreamingHttpResponse(stream(2), content_type="multipart/x-mixed-replace;boundary=frame")

def serve_video(request):
    # Path to your video file
    video_path = os.path.join(settings.BASE_DIR, 'D://Video//1120.mp4')

    # Open the file in binary mode
    with open(video_path, 'rb') as f:
        video_data = f.read()

    # Return the video file as response
    return HttpResponse(video_data, content_type='video/mp4')

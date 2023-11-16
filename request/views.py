from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from request.detech import Detech
from datetime import datetime
import os
import easyocr

from request.serializers import VehicleSerializer
from .models import Vehicle


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



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
    def post(self, request):
        try:
            print('Deleting all vehicles')
            Vehicle.objects.all().delete()
            message = "All vehicles have been deleted."
            return Response({"message": message}, status=status.HTTP_200_OK)
        except Exception as e:
            error_message = f"Error deleting vehicles: {e}"
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

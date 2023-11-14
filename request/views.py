from django.http import JsonResponse
from rest_framework.views import APIView

from request.detech import Detech
from datetime import datetime
import os
import easyocr
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class RootAPI(APIView):
    def get(self, request):
        return JsonResponse({"message": "Hey this is my API running 🥳"})
class DetechAPI(APIView):
    def get(self, request):
        print('running...')
        Detech.DetechLicensePlate()
        return JsonResponse({"message": "Hey this is my API running 🥳"})
    
# class LicensePlateAPI(APIView):
#     def get(self, request):
#         # reader = easyocr.Reader(['en'])
#         # formatted_datetime = datetime.now().strftime("%Y_%m_%d")
#         MEDIA_DIR = os.path.join(BASE_DIR, 'pbl_traffic_be/media')
#         all_files = os.listdir(MEDIA_DIR)
#         data = []
#         for file in all_files:
#             child_file = os.path.join(MEDIA_DIR, file)
#             child_all_files = os.listdir(child_file)
#             for child in child_all_files:
#                  child_level2_file = os.path.join(child_file, child)
#                  child_level2_all_file = os.listdir(child_level2_file)
#                  data.append({
#                     file: {
#                         child: child_level2_all_file
#                     }
#                 })
#             # data.append({
#             #     file: child_all_files
#             # })
           

        
#         # for file in all_files:
#         #     result = reader.readtext(os.path.join(MEDIA_DIR, file))
#         #     rs = [item[1] for item in result]
#         #     data.append({
#         #         'file': file,
#         #         'result': rs
#         #     })
            
#         print('result ==> : ', data) 
        
        
#         return JsonResponse({"message": "Hey this is my API running 🥳", "data": data})
    

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

                binary_data = {}
                for file in binary_files:
                    file_path = os.path.join(binary_folder_path, file)
                    result = reader.readtext(file_path)
                    text_results = [item[1] for item in result]
                    binary_data[file] = text_results

                result_files = os.listdir(result_folder_path) if os.path.exists(result_folder_path) else []

                day_data = {
                    day_folder: {
                        'binary': binary_data,
                        'result': result_files
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
    

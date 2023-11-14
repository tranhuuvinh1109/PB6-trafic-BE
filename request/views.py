from django.http import JsonResponse
from rest_framework.views import APIView

from request.detech import Detech
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
    
class LicensePlateAPI(APIView):
    def get(self, request):
        reader = easyocr.Reader(['en'])
        MEDIA_DIR = os.path.join(BASE_DIR, 'pbl_traffic_be/media/13_11_2023')
        all_files = os.listdir(MEDIA_DIR)
        data = []
        for file in all_files:
            result = reader.readtext(os.path.join(MEDIA_DIR, file))
            rs = [item[1] for item in result]
            data.append({
                'file': file,
                'result': rs
            })
            
        print('result ==> : ', data) 
        
        
        return JsonResponse({"message": "Hey this is my API running 🥳", "data": data})
from django.db import models

class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    license = models.CharField(max_length=255)
    confidence = models.FloatField(default=0.0)
    image_origin = models.CharField(max_length=255)
    image_detect = models.CharField(max_length=255)
    time = models.CharField(max_length=255)
    license_fixed = models.CharField(max_length=255, default='')
    file_name = models.CharField(max_length=255, default='')
    folder_name = models.CharField(max_length=255, default='')
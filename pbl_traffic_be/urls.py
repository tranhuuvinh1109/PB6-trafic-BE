from pathlib import Path
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
import os
BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'pbl_traffic_be/media')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('request.urls')),
]+ static(MEDIA_URL, document_root=MEDIA_ROOT)

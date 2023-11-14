from django.urls import path
from . import views

urlpatterns = [
    path('root/', views.RootAPI.as_view(), name='RootAPI'),
    path('list/', views.LicensePlateAPI.as_view(), name='LicensePlateAPI'),
    path('detech/', views.DetechAPI.as_view(), name='DetechAPI'),
]

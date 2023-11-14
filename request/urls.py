from django.urls import path
from . import views

urlpatterns = [
    path('root/', views.RootAPI.as_view(), name='RootAPI'),
    path('license/', views.LicensePlateAPI.as_view(), name='LicensePlateAPI'),
    path('list/', views.ListFileAPI.as_view(), name='ListFileAPI'),
    path('detech/', views.DetechAPI.as_view(), name='DetechAPI'),
]

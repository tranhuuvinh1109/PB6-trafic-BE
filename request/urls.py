from django.urls import path
from . import views

urlpatterns = [
    path('root/', views.RootAPI.as_view(), name='RootAPI'),
    path('license/', views.LicensePlateAPI.as_view(), name='LicensePlateAPI'),
    path('list/', views.ListFileAPI.as_view(), name='ListFileAPI'),
    path('detech/', views.DetechAPI.as_view(), name='DetechAPI'),
    path('delete-all-vehicle/', views.DeleteAllVehicles.as_view(), name='DeleteAllVehicles'),
    path('vehicles/', views.AllVehiclesAPI.as_view(), name='AllVehiclesAPI'),
    path('update-vehicle/<int:vehicle_id>/', views.UpdateVehicle.as_view(), name='update-vehicle'),
]

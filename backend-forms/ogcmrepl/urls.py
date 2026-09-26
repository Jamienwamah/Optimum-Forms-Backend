from django.urls import path
from .views import get_replacement_employee, create_device_replacement

urlpatterns = [
    path("ogcm/replacement/employee/", get_replacement_employee, name="get_replacement_employee"),
    path("ogcm/replacement/", create_device_replacement, name="create_device_replacement"),
]
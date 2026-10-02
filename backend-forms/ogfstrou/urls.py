from django.urls import path
from .views import get_troubleshoot_employee, create_device_troubleshoot

urlpatterns = [
    path("ogfs/troubleshoot/employee/", get_troubleshoot_employee, name="get_troubleshoot_employee"),
    path("ogfs/troubleshoot/", create_device_troubleshoot, name="create_device_troubleshoot"),
]
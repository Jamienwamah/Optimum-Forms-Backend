from django.urls import path
from .views import get_troubleshoot_employee, create_device_troubleshoot

urlpatterns = [
    path("ost/troubleshoot/employee/", get_troubleshoot_employee, name="get_troubleshoot_employee"),
    path("ost/troubleshoot/", create_device_troubleshoot, name="create_device_troubleshoot"),
]
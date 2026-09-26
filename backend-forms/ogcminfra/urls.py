from django.urls import path
from .views import get_infrastructure_employee, create_device_infrastructure

urlpatterns = [
    path("ogcm/infrastructure/employee/", get_infrastructure_employee, name="get_infrastructure_employee"),
    path("ogcm/infrastructure/", create_device_infrastructure, name="create_device_infrastructure"),
]
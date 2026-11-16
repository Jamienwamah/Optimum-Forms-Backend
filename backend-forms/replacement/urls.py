
from django.urls import path

from .views import DeviceReplacementCreateView


urlpatterns = [

    path(
        "replacement/",
        DeviceReplacementCreateView.as_view(),
        name="device-replacement-create"
    ),

]


from django.urls import path

from .views import DeviceTroubleshootingCreateView


urlpatterns = [

    path(
        "troubleshoot/",
        DeviceTroubleshootingCreateView.as_view(),
        name="device-troubleshooting-create"
    ),

]

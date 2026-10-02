from django.urls import path

from .views import (
    EnclusiaAccessRequestCreateView,
)


urlpatterns = [

    path("user/",EnclusiaAccessRequestCreateView.as_view(),name="enclusia-user-access",
         ),

]

from django.urls import path

from .views import LaptopIssueCreateView


urlpatterns = [

    path(
        "issue/",
        LaptopIssueCreateView.as_view(),
        name="laptop-issue-create"
    ),

]

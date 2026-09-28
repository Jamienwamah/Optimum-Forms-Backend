from django.urls import path
from .views import get_my_profile

urlpatterns = [
    path("me/", get_my_profile, name="my-entra-profile"),
    # path("users/", get_all_users, name="get-all-users"),
]
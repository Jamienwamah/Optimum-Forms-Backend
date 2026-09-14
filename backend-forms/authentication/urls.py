from django.urls import path

from . import views


app_name = "authentication"


urlpatterns = [

    path("login/",views.microsoft_login,name="login"
    ),

    path("callback/",views.microsoft_callback,name="callback"
    ),

    path("user/",views.current_user,name="current_user"
     ),

    path("logout/",views.logout_view,name="logout"
    ),
    #  path("auth/callback/", views.microsoft_callback, name="microsoft_callback"
    # ),
]
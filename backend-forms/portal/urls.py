"""
URL configuration for portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from .views import csrf_token


def api_status(request):
    return JsonResponse({
        "status": "success",
        "message": "Django backend is running."
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/csrf/", csrf_token, name="csrf_token"),
    path("api/v1/entra/", include("entraprofile.urls")),
    path("api/v1/enclusia/", include("enclusia.urls")),
    path("api/v1/access/", include("access_control.urls")),

    path("",api_status,name="api_status"
    ),

    path("auth/", include("authentication.urls")),
    path('api/v1/',include('ogcminfra.urls')),
    path('api/v1/', include('ogcmrepl.urls')),
    path('api/v1/', include('ogcmtrou.urls')),
    path('api/v1/', include('ogfstrou.urls')),
    path('api/v1/', include('osttrou.urls')),

]
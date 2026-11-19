
"""
URL configuration for portal project.
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
    # Django administration
    path("admin/", admin.site.urls),

    # CSRF
    path("api/csrf/", csrf_token, name="csrf_token"),

    # Authentication
    path("auth/", include("authentication.urls")),

    # User identity and access management
    path("api/v1/entra/", include("entraprofile.urls")),
    path("api/v1/enclusia/", include("enclusia.urls")),
    path("api/v1/access/", include("access_control.urls")),

    # Shared company-aware API endpoints
    path("api/v1/", include("infrastructure.urls")),
    path("api/v1/", include("replacement.urls")),
    path("api/v1/", include("troubleshoot.urls")),
    path("api/v1/", include("issue.urls")),

    # Device replacement endpoint
    path("api/v1/ogcm/", include("replacement.urls")),

    # Backend status
    path("", api_status, name="api_status"),
]

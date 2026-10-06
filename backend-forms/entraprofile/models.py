from django.db import models
from django.conf import settings

class EntraProfile(models.Model):
    DASHBOARD_SUPER_ADMIN = "SUPER_ADMIN"
    DASHBOARD_ADMIN = "ADMIN"
    DASHBOARD_APPROVER = "APPROVER"

    DASHBOARD_ROLE_CHOICES = [
        (DASHBOARD_SUPER_ADMIN, "Super Administrator"),
        (DASHBOARD_ADMIN, "Administrator"),
        (DASHBOARD_APPROVER, "Approver"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="entra_profile")
    entra_object_id = models.CharField(max_length=100, unique=True)
    tenant_id = models.CharField(max_length=100)
    display_name = models.CharField(max_length=255, blank=True)
    given_name = models.CharField(max_length=150, blank=True)
    family_name = models.CharField(max_length=150, blank=True)
    job_title = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    employee_id = models.CharField(max_length=100, blank=True)
    entra_roles = models.JSONField(default=list, blank=True)
    dashboard_role = models.CharField(max_length=30, choices=DASHBOARD_ROLE_CHOICES, default=DASHBOARD_APPROVER)
    last_synced = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name
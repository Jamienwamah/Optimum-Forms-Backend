from django.db import models
from django.conf import settings


class EntraProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entra_profile"
    )

    entra_object_id = models.CharField(max_length=100, unique=True)
    tenant_id = models.CharField(max_length=100)
    display_name = models.CharField(max_length=255, blank=True)
    given_name = models.CharField(max_length=150, blank=True)
    family_name = models.CharField(max_length=150, blank=True)
    job_title = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    employee_id = models.CharField(max_length=100, blank=True)

    last_synced = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name
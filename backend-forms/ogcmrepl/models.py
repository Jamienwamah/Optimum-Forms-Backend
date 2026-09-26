from django.db import models
from django.conf import settings

class OGCMDeviceReplacement(models.Model):

    # --------------------------------------------------------
    # EMPLOYEE INFORMATION
    # Retrieved from Microsoft Entra
    # --------------------------------------------------------

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ogcm_device_replacements"
    )

    employee_name = models.CharField(
        max_length=255
    )

    employee_id = models.CharField(
        max_length=100
    )

    employee_department = models.CharField(
        max_length=255
    )

    employee_job_title = models.CharField(
        max_length=255
    )

    # --------------------------------------------------------
    # CURRENT DEVICE INFORMATION
    # --------------------------------------------------------

    asset_tag = models.CharField(
        max_length=100,
        blank=True
    )

    current_device_type = models.CharField(
        max_length=100
    )

    current_brand_model = models.CharField(
        max_length=255
    )

    current_serial_number = models.CharField(
        max_length=255
    )

    reason_for_replacement = models.TextField()

    # --------------------------------------------------------
    # REPLACEMENT REQUIREMENTS
    # --------------------------------------------------------

    requested_device_type = models.CharField(
        max_length=150
    )

    urgency_level = models.CharField(
        max_length=50
    )

    justification = models.TextField()

    required_date = models.DateField()

    # --------------------------------------------------------
    # AUTHORIZATION
    # --------------------------------------------------------

    authorization_agreed = models.BooleanField(
        default=False
    )

    # --------------------------------------------------------
    # EMPLOYEE SIGNATURE
    # --------------------------------------------------------

    employee_signature = models.CharField(
        max_length=255
    )

    employee_signature_date = models.DateField()

    # --------------------------------------------------------
    # SYSTEM DATES
    # --------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.employee_name} - "
            f"{self.current_device_type} Replacement"
        )

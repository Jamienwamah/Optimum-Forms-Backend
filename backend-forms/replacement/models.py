
from django.conf import settings
from django.db import models


class DeviceReplacementRequest(models.Model):

    STATUS_CHOICES = [
        ("Submitted", "Submitted"),
        ("In Progress", "In Progress"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Completed", "Completed"),
        ("Closed", "Closed"),
    ]

    DEVICE_TYPE_CHOICES = [
        ("Laptop", "Laptop"),
        ("Desktop", "Desktop / Workstation"),
        ("Mobile", "Mobile / Tablet"),
        ("Peripheral", "Peripheral / Other"),
    ]

    URGENCY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    # EMPLOYEE INFORMATION
    requester_name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=100)

    # CURRENT DEVICE INFORMATION
    asset_tag = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    device_type = models.CharField(
        max_length=50,
        choices=DEVICE_TYPE_CHOICES
    )

    brand_model = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255)

    reason_for_replacement = models.TextField()

    # REPLACEMENT REQUIREMENTS
    requested_device_type = models.CharField(
        max_length=50,
        choices=DEVICE_TYPE_CHOICES
    )

    urgency_level = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES
    )

    justification = models.TextField()

    required_date = models.DateField()

    # APPROVAL STATUS
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Submitted"
    )

    # SYSTEM INFORMATION
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device_replacement_requests"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Device Replacement Request"
        verbose_name_plural = "Device Replacement Requests"

    def __str__(self):
        return (
            f"{self.requester_name} - "
            f"{self.brand_model} - "
            f"{self.status}"
        )

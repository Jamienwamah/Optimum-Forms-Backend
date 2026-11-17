
from django.conf import settings
from django.db import models


class DeviceTroubleshootingRequest(models.Model):

    # ==========================================================
    # COMPANY
    # ==========================================================

    class Company(models.TextChoices):
        OGCM = "OGCM", "Optimum Global Capital"
        OGFS = "OGFS", "Optimum Global Financial Services"
        OST = "OST", "Optimum Securities and Trust"

    company = models.CharField(
        max_length=4,
        choices=Company.choices,
        db_index=True
    )

    # ==========================================================
    # REQUEST STATUS
    # ==========================================================

    STATUS_CHOICES = [
        ("Submitted", "Submitted"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Rejected", "Rejected"),
        ("Closed", "Closed"),
    ]

    DEVICE_TYPE_CHOICES = [
        ("Laptop", "Laptop"),
        ("Desktop", "Desktop / Workstation"),
        ("Mobile", "Mobile / Tablet"),
        ("Peripheral", "Peripheral / Display"),
    ]

    # ==========================================================
    # EMPLOYEE INFORMATION
    # ==========================================================

    requester_name = models.CharField(max_length=255)

    department = models.CharField(max_length=255)

    job_title = models.CharField(max_length=255)

    employee_id = models.CharField(max_length=100)

    # ==========================================================
    # DEVICE INFORMATION
    # ==========================================================

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

    operating_system = models.CharField(max_length=255)

    # ==========================================================
    # ISSUE INFORMATION
    # ==========================================================

    date_reported = models.DateField()

    reported_by = models.CharField(max_length=255)

    description = models.TextField()

    start_date = models.DateField()

    troubleshooting_attempted = models.BooleanField(default=False)

    attempted_details = models.TextField(
        blank=True,
        null=True
    )

    # ==========================================================
    # REQUEST STATUS
    # ==========================================================

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Submitted"
    )

    # ==========================================================
    # SYSTEM INFORMATION
    # ==========================================================

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device_troubleshooting_requests"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # ==========================================================
    # MODEL CONFIGURATION
    # ==========================================================

    class Meta:

        ordering = ["-created_at"]

        verbose_name = "Device Troubleshooting Request"

        verbose_name_plural = "Device Troubleshooting Requests"

        indexes = [
            models.Index(
                fields=["company", "-created_at"],
                name="trouble_company_created_idx"
            ),
            models.Index(
                fields=["company", "status"],
                name="trouble_company_status_idx"
            ),
        ]

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __str__(self):

        return (
            f"{self.requester_name} - "
            f"{self.brand_model} - "
            f"{self.company} - "
            f"{self.status}"
        )

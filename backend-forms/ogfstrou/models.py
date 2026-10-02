from django.conf import settings
from django.db import models


class OGFSDeviceTroubleshooting(models.Model):

    DEVICE_TYPE_CHOICES = [
        ("Laptop", "Laptop"),
        ("Desktop", "Desktop / Workstation"),
        ("Mobile", "Mobile / Tablet"),
        ("Peripheral", "Peripheral / Other"),
    ]

    STATUS_CHOICES = [
        ("Submitted", "Submitted"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Closed", "Closed"),
    ]

    # ============================================================
    # SYSTEM INFORMATION
    # ============================================================

    form_reference = models.CharField(
        max_length=50,
        default="IT-TS-2026",
        editable=False
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ogfs_troubleshooting_requests"
    )

    current_date = models.DateTimeField(
        auto_now_add=True
    )

    created_at = models.DateTimeField(
    auto_now_add=True
)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Submitted"
    )

    # ============================================================
    # EMPLOYEE INFORMATION
    # ============================================================

    employee_name = models.CharField(
        max_length=255
    )

    employee_department = models.CharField(
        max_length=255
    )

    employee_job_title = models.CharField(
        max_length=255
    )

    # Employee enters this manually.
    # It is NOT populated from Entra.
    employee_id = models.CharField(
        max_length=100
    )

    # ============================================================
    # DEVICE INFORMATION
    # ============================================================

    asset_tag = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    device_type = models.CharField(
        max_length=50,
        choices=DEVICE_TYPE_CHOICES
    )

    brand_model = models.CharField(
        max_length=255
    )

    serial_number = models.CharField(
        max_length=255
    )

    operating_system = models.CharField(
        max_length=255
    )

    # ============================================================
    # ISSUE INFORMATION
    # ============================================================

    date_reported = models.DateField()

    reported_by = models.CharField(
        max_length=255
    )

    description = models.TextField()

    start_date = models.DateField()

    troubleshooting_attempted = models.BooleanField(
        default=False
    )

    attempted_details = models.TextField(
        blank=True,
        null=True
    )

    # ============================================================
    # CONSENT
    # ============================================================

    consent_agreed = models.BooleanField(
        default=False
    )

    # ============================================================
    # EMPLOYEE SIGNATURE
    # ============================================================

    employee_signature = models.CharField(
        max_length=255
    )

    employee_signature_date = models.DateField()

    # ============================================================
    # IT REPRESENTATIVE
    # ============================================================

    it_representative = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    it_title = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    it_signature = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    it_signature_date = models.DateField(
        blank=True,
        null=True
    )

    # ============================================================
    # OFFICIAL USE / IT ASSESSMENT
    # ============================================================

    received_by = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    date_received = models.DateField(
        blank=True,
        null=True
    )

    # Assessment
    assessment_hardware = models.BooleanField(
        default=False
    )

    assessment_software = models.BooleanField(
        default=False
    )

    assessment_network = models.BooleanField(
        default=False
    )

    assessment_os = models.BooleanField(
        default=False
    )

    assessment_malware = models.BooleanField(
        default=False
    )

    assessment_user_config = models.BooleanField(
        default=False
    )

    assessment_other = models.TextField(
        blank=True,
        null=True
    )

    # ============================================================
    # TROUBLESHOOTING PERFORMED BY IT
    # ============================================================

    troubleshooting_hw_diag = models.BooleanField(
        default=False
    )

    troubleshooting_os_repair = models.BooleanField(
        default=False
    )

    troubleshooting_driver_updates = models.BooleanField(
        default=False
    )

    troubleshooting_sw_reinstall = models.BooleanField(
        default=False
    )

    troubleshooting_malware_removal = models.BooleanField(
        default=False
    )

    troubleshooting_win_updates = models.BooleanField(
        default=False
    )

    troubleshooting_data_backup = models.BooleanField(
        default=False
    )

    troubleshooting_pwd_reset = models.BooleanField(
        default=False
    )

    troubleshooting_hw_replacement = models.BooleanField(
        default=False
    )

    parts_replaced = models.TextField(
        blank=True,
        null=True
    )

    outcome = models.TextField(
        blank=True,
        null=True
    )

    date_returned = models.DateField(
        blank=True,
        null=True
    )

    returned_by = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    user_confirmation = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    confirmation_date = models.DateField(
        blank=True,
        null=True
    )

    additional_comments = models.TextField(
        blank=True,
        null=True
    )

    # ============================================================
    # TIMESTAMPS
    # ============================================================

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Device Troubleshooting Request"
        verbose_name_plural = "Device Troubleshooting Requests"

    def __str__(self):
        return (
            f"{self.form_reference} - "
            f"{self.employee_name} - "
            f"{self.serial_number}"
        )
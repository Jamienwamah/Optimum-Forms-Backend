from django.conf import settings
from django.db import models


class InfrastructureReceipt(models.Model):

    # ==========================================================
    # REQUEST STATUS
    # ==========================================================

    STATUS_CHOICES = [
        ("Submitted", "Submitted"),
        ("In Progress", "In Progress"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Completed", "Completed"),
        ("Closed", "Closed"),
    ]


    # ==========================================================
    # INFRASTRUCTURE CATEGORIES
    # ==========================================================

    CATEGORY_CHOICES = [
        ("Server", "Server"),
        ("Desktop Computer", "Desktop Computer"),
        ("Laptop", "Laptop"),
        ("Monitor", "Monitor"),
        ("Printer", "Printer"),
        ("Network Switch", "Network Switch"),
        ("Router", "Router"),
        ("Firewall", "Firewall"),
        ("Wireless Access Point", "Wireless Access Point"),
        ("UPS", "UPS"),
        ("NAS/SAN Storage", "NAS/SAN Storage"),
        ("CCTV Equipment", "CCTV Equipment"),
        ("Biometric", "Biometric"),
    ]


    # ==========================================================
    # INSPECTION PHYSICAL CONDITION
    # ==========================================================

    PHYSICAL_CONDITION_CHOICES = [
        ("New / Intact", "New / Intact"),
        ("Good Condition", "Good Condition"),
        ("Damaged Box", "Damaged Box"),
        ("Defective", "Defective"),
    ]


    # ==========================================================
    # REQUEST INFORMATION
    # ==========================================================

    request_date = models.DateField(
        auto_now_add=True
    )

    requester_name = models.CharField(
        max_length=255
    )

    document_no = models.CharField(
        max_length=100
    )

    date_received = models.DateField()


    # ==========================================================
    # PROCUREMENT INFORMATION
    # ==========================================================

    asset_tag = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    po_number = models.CharField(
        max_length=100
    )

    invoice_number = models.CharField(
        max_length=100
    )

    vendor_supplier = models.CharField(
        max_length=255
    )

    delivery_note_number = models.CharField(
        max_length=100
    )

    procured_by = models.CharField(
        max_length=255
    )

    funding_source = models.CharField(
        max_length=255,
        blank=True
    )


    # ==========================================================
    # INFRASTRUCTURE AND ASSET DETAILS
    # ==========================================================

    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES
    )

    brand_model = models.CharField(
        max_length=255
    )

    serial_number = models.CharField(
        max_length=255
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    specifications = models.TextField(
        blank=True
    )


    # ==========================================================
    # INSPECTION AND QUALITY CHECK
    # ==========================================================

    physical_condition = models.CharField(
        max_length=100,
        choices=PHYSICAL_CONDITION_CHOICES
    )

    accessories_included = models.BooleanField(
        default=False
    )

    passed_inspection = models.BooleanField(
        default=False
    )

    inspected_by = models.CharField(
        max_length=255
    )

    inspection_date = models.DateField()

    notes = models.TextField(
        blank=True
    )


    # ==========================================================
    # APPROVAL WORKFLOW
    # ==========================================================

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Submitted"
    )


    # ==========================================================
    # AUTHENTICATED DJANGO USER
    # ==========================================================

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infrastructure_receipts"
    )


    # ==========================================================
    # RECORD TIMESTAMPS
    # ==========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    # ==========================================================
    # MODEL CONFIGURATION
    # ==========================================================

    class Meta:

        ordering = ["-created_at"]

        verbose_name = "Infrastructure Receipt"

        verbose_name_plural = "Infrastructure Receipts"


    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __str__(self):

        return (
            f"{self.document_no} - "
            f"{self.brand_model} - "
            f"{self.status}"
        )
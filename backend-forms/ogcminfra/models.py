from django.db import models
from django.conf import settings


class OGCMInfrastructureReceipt(models.Model):

    document_no = models.CharField(
        max_length=100,
        unique=True
    )

    date_received = models.DateField()

    # Authenticated user who created/submitted the receipt
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ogcm_infrastructure_receipts",
        null=True,
        blank=True
    )

    # Employee Information
    employee_name = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    employee_id = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    employee_department = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    employee_job_title = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    # Procurement
    asset_tag = models.CharField(
        max_length=100,
        blank=True,
        default=""
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
        blank=True,
        default=""
    )

    # Infrastructure
    category = models.CharField(
        max_length=100
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
        blank=True,
        default=""
    )

    # Inspection
    physical_condition = models.CharField(
        max_length=100
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
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
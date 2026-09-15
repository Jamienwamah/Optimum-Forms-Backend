from django.db import models
from django.conf import settings

class OGCMInfrastructureReceipt(models.Model):
    document_no = models.CharField(max_length=100, unique=True)
    date_received = models.DateField()

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ogcm_infrastructure_receipts', null=True, blank=True)
    user_name = models.CharField(max_length=255, null=True, blank=True)
    user_email = models.EmailField(null=True, blank=True)
    user_department = models.CharField(max_length=255, null=True, blank=True)
    user_job_title = models.CharField(max_length=255, null=True, blank=True)
    user_company = models.CharField(max_length=255, null=True, blank=True)

    asset_tag = models.CharField(max_length=100, blank=True, null=True)
    po_number = models.CharField(max_length=100)
    invoice_number = models.CharField(max_length=100)
    vendor_supplier = models.CharField(max_length=255)
    delivery_note_number = models.CharField(max_length=100)
    procured_by = models.CharField(max_length=255)
    funding_source = models.CharField(max_length=255, blank=True, null=True)

    category = models.CharField(max_length=100)
    brand_model = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    specifications = models.TextField(blank=True, null=True)

    physical_condition = models.CharField(max_length=100)
    accessories_included = models.BooleanField(default=True)
    passed_inspection = models.BooleanField(default=True)
    inspected_by = models.CharField(max_length=255)
    inspection_date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OGCM Infrastructure Receipt'
        verbose_name_plural = 'OGCM Infrastructure Receipts'

    def __str__(self):
        return f"{self.document_no} - {self.brand_model}"
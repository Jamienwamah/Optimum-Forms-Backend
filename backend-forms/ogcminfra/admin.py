from django.contrib import admin

from .models import OGCMInfrastructureReceipt


@admin.register(OGCMInfrastructureReceipt)
class OGCMInfrastructureReceiptAdmin(admin.ModelAdmin):

    list_display = (
        'document_no',
        'category',
        'brand_model',
        'serial_number',
        'quantity',
        'vendor_supplier',
        'passed_inspection',
        'inspection_date',
        'created_at',
    )

    search_fields = (
        'document_no',
        'asset_tag',
        'po_number',
        'invoice_number',
        'vendor_supplier',
        'serial_number',
        'brand_model',
    )

    list_filter = ('category','physical_condition','passed_inspection','accessories_included','inspection_date','date_received',
    )

    readonly_fields = ('created_at','updated_at',
    )
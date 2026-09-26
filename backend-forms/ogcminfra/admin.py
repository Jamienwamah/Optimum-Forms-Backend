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
        'delivery_note_number',
        'procured_by',
        'category',
        'brand_model',
        'serial_number',
        'inspected_by',
    )

    list_filter = (
        'category',
        'physical_condition',
        'accessories_included',
        'passed_inspection',
        'inspection_date',
        'date_received',
        'created_at',
    )

    readonly_fields = (
        'created_at',
    )

    ordering = (
        '-created_at',
    )
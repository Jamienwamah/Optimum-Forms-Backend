from django.contrib import admin

from .models import InfrastructureReceipt


@admin.register(InfrastructureReceipt)
class InfrastructureReceiptAdmin(admin.ModelAdmin):

    list_display = (
        "document_no",
        "requester_name",
        "category",
        "brand_model",
        "serial_number",
        "quantity",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "category",
        "physical_condition",
        "passed_inspection",
        "created_at",
    )

    search_fields = (
        "document_no",
        "requester_name",
        "asset_tag",
        "po_number",
        "invoice_number",
        "vendor_supplier",
        "serial_number",
        "brand_model",
    )

    readonly_fields = (
        "request_date",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )
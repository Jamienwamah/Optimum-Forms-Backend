
from django.contrib import admin

from .models import DeviceTroubleshootingRequest


@admin.register(DeviceTroubleshootingRequest)
class DeviceTroubleshootingRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "requester_name",
        "department",
        "device_type",
        "brand_model",
        "serial_number",
        "operating_system",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "device_type",
        "department",
        "troubleshooting_attempted",
        "created_at",
    )

    search_fields = (
        "requester_name",
        "employee_id",
        "department",
        "asset_tag",
        "brand_model",
        "serial_number",
        "operating_system",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

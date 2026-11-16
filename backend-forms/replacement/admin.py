
from django.contrib import admin

from .models import DeviceReplacementRequest


@admin.register(DeviceReplacementRequest)
class DeviceReplacementRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "requester_name",
        "department",
        "device_type",
        "brand_model",
        "serial_number",
        "requested_device_type",
        "urgency_level",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "device_type",
        "requested_device_type",
        "urgency_level",
        "department",
        "created_at",
    )

    search_fields = (
        "requester_name",
        "employee_id",
        "department",
        "asset_tag",
        "brand_model",
        "serial_number",
        "reason_for_replacement",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

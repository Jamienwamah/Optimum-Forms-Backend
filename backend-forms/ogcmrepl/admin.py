from django.contrib import admin
from .models import OGCMDeviceReplacement


@admin.register(OGCMDeviceReplacement)
class OGCMDeviceReplacementAdmin(admin.ModelAdmin):

    list_display = (
        "employee_name",
        "employee_id",
        "employee_department",
        "current_device_type",
        "current_brand_model",
        "current_serial_number",
        "requested_device_type",
        "urgency_level",
        "required_date",
        "authorization_agreed",
        "created_at",
    )

    search_fields = (
        "employee_name",
        "employee_id",
        "employee_department",
        "employee_job_title",
        "asset_tag",
        "current_brand_model",
        "current_serial_number",
        "requested_device_type",
    )

    list_filter = (
        "employee_department",
        "current_device_type",
        "requested_device_type",
        "urgency_level",
        "authorization_agreed",
        "required_date",
        "created_at",
    )

    readonly_fields = (
        "created_by",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Employee Information",
            {
                "fields": (
                    "created_by",
                    "employee_name",
                    "employee_id",
                    "employee_department",
                    "employee_job_title",
                )
            },
        ),

        (
            "Current Device Information",
            {
                "fields": (
                    "asset_tag",
                    "current_device_type",
                    "current_brand_model",
                    "current_serial_number",
                    "reason_for_replacement",
                )
            },
        ),

        (
            "Replacement Requirements",
            {
                "fields": (
                    "requested_device_type",
                    "urgency_level",
                    "justification",
                    "required_date",
                )
            },
        ),

        (
            "Authorization",
            {
                "fields": (
                    "authorization_agreed",
                )
            },
        ),

        (
            "Employee Signature",
            {
                "fields": (
                    "employee_signature",
                    "employee_signature_date",
                )
            },
        ),

        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
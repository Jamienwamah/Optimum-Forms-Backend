from django.contrib import admin
from .models import OGFSDeviceTroubleshooting


@admin.register(OGFSDeviceTroubleshooting)
class OGFSDeviceTroubleshootingAdmin(admin.ModelAdmin):

    list_display = (
        "form_reference",
        "employee_name",
        "employee_id",
        "employee_department",
        "device_type",
        "brand_model",
        "serial_number",
        "status",
        "date_reported",
        "created_at",
    )

    search_fields = (
        "form_reference",
        "employee_name",
        "employee_id",
        "employee_department",
        "employee_job_title",
        "asset_tag",
        "brand_model",
        "serial_number",
        "operating_system",
        "reported_by",
        "it_representative",
        "received_by",
    )

    list_filter = (
        "status",
        "device_type",
        "employee_department",
        "troubleshooting_attempted",
        "consent_agreed",
        "date_reported",
        "created_at",
    )

    readonly_fields = (
        "form_reference",
        "created_by",
        "current_date",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    fieldsets = (

        (
            "System Information",
            {
                "fields": (
                    "form_reference",
                    "created_by",
                    "current_date",
                    "created_at",
                    "updated_at",
                    "status",
                )
            },
        ),

        (
            "Employee Information",
            {
                "fields": (
                    "employee_name",
                    "employee_department",
                    "employee_job_title",
                    "employee_id",
                )
            },
        ),

        (
            "Device Information",
            {
                "fields": (
                    "asset_tag",
                    "device_type",
                    "brand_model",
                    "serial_number",
                    "operating_system",
                )
            },
        ),

        (
            "Issue Information",
            {
                "fields": (
                    "date_reported",
                    "reported_by",
                    "description",
                    "start_date",
                    "troubleshooting_attempted",
                    "attempted_details",
                )
            },
        ),

        (
            "Employee Consent",
            {
                "fields": (
                    "consent_agreed",
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
            "IT Representative",
            {
                "fields": (
                    "it_representative",
                    "it_title",
                    "it_signature",
                    "it_signature_date",
                )
            },
        ),

        (
            "Official Use / IT Assessment",
            {
                "fields": (
                    "received_by",
                    "date_received",
                    "assessment_hardware",
                    "assessment_software",
                    "assessment_network",
                    "assessment_os",
                    "assessment_malware",
                    "assessment_user_config",
                    "assessment_other",
                )
            },
        ),

        (
            "Troubleshooting Performed by IT",
            {
                "fields": (
                    "troubleshooting_hw_diag",
                    "troubleshooting_os_repair",
                    "troubleshooting_driver_updates",
                    "troubleshooting_sw_reinstall",
                    "troubleshooting_malware_removal",
                    "troubleshooting_win_updates",
                    "troubleshooting_data_backup",
                    "troubleshooting_pwd_reset",
                    "troubleshooting_hw_replacement",
                    "parts_replaced",
                )
            },
        ),

        (
            "Resolution / Return",
            {
                "fields": (
                    "outcome",
                    "date_returned",
                    "returned_by",
                    "user_confirmation",
                    "confirmation_date",
                    "additional_comments",
                )
            },
        ),
    )
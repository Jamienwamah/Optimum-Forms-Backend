
from django.contrib import admin

from .models import LaptopIssue


@admin.register(LaptopIssue)
class LaptopIssueAdmin(admin.ModelAdmin):

    list_display = (
        "document_no",
        "requester_name",
        "department",
        "brand_model",
        "serial_number",
        "date_issued",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "department",
        "date_issued",
        "created_at",
    )

    search_fields = (
        "document_no",
        "requester_name",
        "department",
        "job_title",
        "employee_id",
        "laptop_details",
        "brand_model",
        "serial_number",
    )

    readonly_fields = (
        "request_date",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

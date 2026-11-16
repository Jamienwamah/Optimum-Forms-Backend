from django.contrib import admin
from .models import EnclusiaAccessRequest


@admin.register(EnclusiaAccessRequest)
class EnclusiaAccessRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "requester_name",
        "access_for_name",
        "access_for_email",
        "employee_department",
        # "expiration_type",
        "access_required",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        # "expiration_type",
        "access_required",
        "employee_department",
        "created_at",
    )

    search_fields = (
        "requester_name",
        "access_for_name",
        "access_for_email",
        "employee_name",
        "employee_id",
        "employee_department",
        "access_required",
        "justification",
    )

    readonly_fields = (
        "request_date",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"
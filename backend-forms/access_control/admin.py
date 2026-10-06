from django.contrib import admin
from .models import ApprovalRequest


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "form_code",
        "user",
        "department",
        "status",
        "submitted_at",
        "reviewed_at",
    )

    list_filter = (
        "status",
        "department",
        "form_code",
    )

    search_fields = (
        "form_code",
        "department",
        "department_email",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "submitted_at",
        "reviewed_at",
    )
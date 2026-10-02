from django.contrib import admin
from .models import EntraProfile


@admin.register(EntraProfile)
class EntraProfileAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "user",
        "department",
        "job_title",
        "employee_id",
        "tenant_id",
        "last_synced",
    )

    search_fields = (
        "display_name",
        "given_name",
        "family_name",
        "employee_id",
        "department",
        "job_title",
        "entra_object_id",
        "user__username",
        "user__email",
    )

    list_filter = (
        "department",
        "job_title",
        "last_synced",
    )

    readonly_fields = (
        "entra_object_id",
        "tenant_id",
        "last_synced",
        "created_at",
    )

    ordering = ("-last_synced",)

    fieldsets = (
        (
            "User",
            {
                "fields": (
                    "user",
                    "display_name",
                    "given_name",
                    "family_name",
                    "employee_id",
                )
            },
        ),
        (
            "Organisation",
            {
                "fields": (
                    "department",
                    "job_title",
                )
            },
        ),
        (
            "Microsoft Entra ID",
            {
                "fields": (
                    "entra_object_id",
                    "tenant_id",
                )
            },
        ),
        (
            "Sync Information",
            {
                "fields": (
                    "last_synced",
                    "created_at",
                )
            },
        ),
    )
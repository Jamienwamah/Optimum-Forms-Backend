from django.contrib import admin

from .models import EnclusiaAccessRequest


@admin.register(EnclusiaAccessRequest)
class EnclusiaAccessRequestAdmin(admin.ModelAdmin):

    # ---------------------------------------------------------
    # LIST VIEW
    # ---------------------------------------------------------

    list_display = (
        "id",
        "request_date",
        "access_for_name",
        "access_for_email",
        "employee_department",
        "rolecode",
        "role",
        "status",
        "created_by",
        "created_at",
    )

    list_filter = (
        "status",
        "rolecode",
        "role",
        "employee_department",
        "request_date",
        "created_at",
    )

    search_fields = (
        "access_for_name",
        "access_for_email",
        "employee_name",
        "employee_id",
        "employee_department",
        "employee_job_title",
        "requester_name",
        "role",
        "rolecode",
        "role_description",
        "reason",
    )

    ordering = (
        "-created_at",
    )


    # ---------------------------------------------------------
    # FORM FIELDS
    # ---------------------------------------------------------

    fieldsets = (

        (
            "Request Information",
            {
                "fields": (
                    "request_date",
                    "status",
                    "created_by",
                )
            },
        ),

        (
            "Requester Information",
            {
                "fields": (
                    "requester_name",
                )
            },
        ),

        (
            "Access For",
            {
                "fields": (
                    "access_for_name",
                    "access_for_email",
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
            "Enclusia Cloud Platform Access",
            {
                "fields": (
                    "rolecode",
                    "role",
                    "role_description",
                    "reason",
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


    # ---------------------------------------------------------
    # READ-ONLY SYSTEM FIELDS
    # ---------------------------------------------------------

    readonly_fields = (
        "request_date",
        "created_by",
        "created_at",
        "updated_at",
    )


    # ---------------------------------------------------------
    # DATE HIERARCHY
    # ---------------------------------------------------------

    date_hierarchy = "request_date"


    # ---------------------------------------------------------
    # PAGINATION
    # ---------------------------------------------------------

    list_per_page = 25


    # ---------------------------------------------------------
    # SAVE BEHAVIOUR
    # ---------------------------------------------------------

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):
        """
        Automatically assign the authenticated
        Django user when creating a request
        directly from Django Admin.
        """

        if not obj.created_by:
            obj.created_by = request.user

        super().save_model(
            request,
            obj,
            form,
            change
        )
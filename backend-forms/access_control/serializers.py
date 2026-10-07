from rest_framework import serializers

from .models import ApprovalRequest


class ApprovalRequestSerializer(
    serializers.ModelSerializer
):

    # ========================================================
    # REQUEST CREATOR
    # ========================================================

    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    user_department = serializers.SerializerMethodField()
    user_job_title = serializers.SerializerMethodField()

    # ========================================================
    # PERSON THE REQUEST IS FOR
    # ========================================================

    requested_for_name = serializers.CharField(
        read_only=True
    )

    requested_for_email = serializers.EmailField(
        read_only=True
    )

    requested_for_department = serializers.CharField(
        read_only=True
    )

    # ========================================================
    # REVIEWER
    # ========================================================

    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:

        model = ApprovalRequest

        fields = [
            "id",

            # Request creator
            "user",
            "user_name",
            "user_email",
            "user_department",
            "user_job_title",

            # Person requested for
            "requested_for_name",
            "requested_for_email",
            "requested_for_department",

            # Approval request
            "form_code",
            "department",
            "department_email",
            "reason",
            "submission_data",
            "status",
            "submitted_at",
            "reviewed_at",
            "reviewed_by",
            "reviewed_by_name",
            "approver_comment",
        ]

        read_only_fields = [
            "id",

            # Request creator
            "user",
            "user_name",
            "user_email",
            "user_department",
            "user_job_title",

            # Person requested for
            "requested_for_name",
            "requested_for_email",
            "requested_for_department",

            # Approval information
            "department",
            "department_email",
            "status",
            "submitted_at",
            "reviewed_at",
            "reviewed_by",
            "reviewed_by_name",
            "approver_comment",
        ]

    def get_user_name(self, obj):

        user = obj.user

        full_name = (
            getattr(
                user,
                "get_full_name",
                lambda: "",
            )()
        )

        if full_name:
            return full_name

        return (
            getattr(
                user,
                "username",
                None,
            )
            or getattr(
                user,
                "email",
                "",
            )
        )

    def get_user_email(self, obj):

        return getattr(
            obj.user,
            "email",
            "",
        )

    def get_user_department(self, obj):

        return getattr(
            obj.user,
            "department",
            "",
        )

    def get_user_job_title(self, obj):

        return getattr(
            obj.user,
            "job_title",
            "",
        )

    def get_reviewed_by_name(self, obj):

        if not obj.reviewed_by:
            return ""

        full_name = (
            getattr(
                obj.reviewed_by,
                "get_full_name",
                lambda: "",
            )()
        )

        return (
            full_name
            or getattr(
                obj.reviewed_by,
                "username",
                "",
            )
        )


class CreateApprovalRequestSerializer(
    serializers.Serializer
):

    form_code = serializers.CharField(
        max_length=100
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    submission_data = serializers.JSONField(
        required=False,
        default=dict,
    )
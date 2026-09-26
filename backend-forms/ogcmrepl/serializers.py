from rest_framework import serializers

from .models import OGCMDeviceReplacement


class OGCMDeviceReplacementSerializer(serializers.ModelSerializer):

    class Meta:
        model = OGCMDeviceReplacement

        fields = [
            "id",

            # Employee information
            "employee_name",
            "employee_id",
            "employee_department",
            "employee_job_title",

            # Current device
            "asset_tag",
            "current_device_type",
            "current_brand_model",
            "current_serial_number",
            "reason_for_replacement",

            # Replacement requirements
            "requested_device_type",
            "urgency_level",
            "justification",
            "required_date",

            # Authorization
            "authorization_agreed",

            # Signature
            "employee_signature",
            "employee_signature_date",

            # System
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",

            # These are controlled by Microsoft Entra
            "employee_name",
            "employee_id",
            "employee_department",
            "employee_job_title",

            # System fields
            "created_at",
            "updated_at",
        ]

    def validate_authorization_agreed(self, value):

        if value is not True:
            raise serializers.ValidationError(
                "You must accept the authorization."
            )

        return value

    def create(self, validated_data):

        request = self.context["request"]

        # ----------------------------------------------------
        # GET THE LOGGED-IN USER'S ENTRA PROFILE
        # ----------------------------------------------------

        profile = getattr(
            request.user,
            "entra_profile",
            None
        )

        if not profile:
            raise serializers.ValidationError(
                "Microsoft Entra profile not found for this user."
            )

        # ----------------------------------------------------
        # OVERRIDE EMPLOYEE INFORMATION
        # WITH MICROSOFT ENTRA INFORMATION
        # ----------------------------------------------------

        validated_data["created_by"] = request.user

        validated_data["employee_name"] = (
            profile.display_name
        )

        validated_data["employee_id"] = (
            profile.employee_id
        )

        validated_data["employee_department"] = (
            profile.department
        )

        validated_data["employee_job_title"] = (
            profile.job_title
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        return OGCMDeviceReplacement.objects.create(
            **validated_data
        )

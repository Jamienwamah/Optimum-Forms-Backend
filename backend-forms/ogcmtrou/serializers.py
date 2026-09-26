from rest_framework import serializers

from .models import DeviceTroubleshooting
from authentication.models import EntraProfile


class DeviceTroubleshootingSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceTroubleshooting

        fields = [
            # System
            "id",
            "form_reference",
            "current_date",
            "status",

            # Employee
            "employee_name",
            "employee_department",
            "employee_job_title",
            "employee_id",

            # Device
            "asset_tag",
            "device_type",
            "brand_model",
            "serial_number",
            "operating_system",

            # Issue
            "date_reported",
            "reported_by",
            "description",
            "start_date",
            "troubleshooting_attempted",
            "attempted_details",

            # Consent
            "consent_agreed",

            # Employee signature
            "employee_signature",
            "employee_signature_date",

            # IT
            "it_representative",
            "it_title",
            "it_signature",
            "it_signature_date",

            # Official use
            "received_by",
            "date_received",

            "assessment_hardware",
            "assessment_software",
            "assessment_network",
            "assessment_os",
            "assessment_malware",
            "assessment_user_config",
            "assessment_other",

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
            "outcome",
            "date_returned",
            "returned_by",
            "user_confirmation",
            "confirmation_date",
            "additional_comments",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "form_reference",
            "current_date",
            "status",

            # These are controlled by Entra
            "employee_name",
            "employee_department",
            "employee_job_title",

            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        if not attrs.get("consent_agreed"):
            raise serializers.ValidationError({
                "consent_agreed": (
                    "You must agree to the IT diagnosis "
                    "and remediation authorization."
                )
            })

        return attrs

    def create(self, validated_data):

        request = self.context["request"]

        try:
            entra_profile = EntraProfile.objects.get(
                user=request.user
            )
        except EntraProfile.DoesNotExist:
            raise serializers.ValidationError({
                "profile": (
                    "Your Entra ID profile could not be found."
                )
            })

        # ========================================================
        # FORCE THESE VALUES FROM ENTRA
        # ========================================================

        validated_data["employee_name"] = (
            entra_profile.display_name
        )

        validated_data["employee_department"] = (
            entra_profile.department
        )

        validated_data["employee_job_title"] = (
            entra_profile.job_title
        )

        # Employee ID intentionally comes from the submitted form.
        # We DO NOT use entra_profile.employee_id here.

        validated_data["created_by"] = request.user

        return DeviceTroubleshooting.objects.create(
            **validated_data
        )
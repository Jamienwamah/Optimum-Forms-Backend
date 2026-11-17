
from rest_framework import serializers

from .models import DeviceTroubleshootingRequest


# ==========================================================
# EMPLOYEE INFORMATION SERIALIZER
# ==========================================================

class EmployeeSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=255)

    department = serializers.CharField(max_length=255)

    jobTitle = serializers.CharField(max_length=255)

    employeeId = serializers.CharField(max_length=100)


# ==========================================================
# DEVICE INFORMATION SERIALIZER
# ==========================================================

class DeviceSerializer(serializers.Serializer):

    assetTag = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True
    )

    deviceType = serializers.ChoiceField(
        choices=[
            "Laptop",
            "Desktop",
            "Mobile",
            "Peripheral"
        ]
    )

    brandModel = serializers.CharField(max_length=255)

    serialNumber = serializers.CharField(max_length=255)

    operatingSystem = serializers.CharField(max_length=255)


# ==========================================================
# ISSUE INFORMATION SERIALIZER
# ==========================================================

class IssueSerializer(serializers.Serializer):

    dateReported = serializers.DateField()

    reportedBy = serializers.CharField(max_length=255)

    description = serializers.CharField()

    startDate = serializers.DateField()

    troubleshootingAttempted = serializers.BooleanField()

    attemptedDetails = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )


# ==========================================================
# MAIN DEVICE TROUBLESHOOTING SERIALIZER
# ==========================================================

class DeviceTroubleshootingSerializer(serializers.Serializer):

    # ------------------------------------------------------
    # COMPANY
    # ------------------------------------------------------

    company = serializers.ChoiceField(
        choices=DeviceTroubleshootingRequest.Company.choices,
        required=True
    )

    # ------------------------------------------------------
    # CURRENT DATE
    # ------------------------------------------------------

    currentDate = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True
    )

    # ------------------------------------------------------
    # EMPLOYEE INFORMATION
    # ------------------------------------------------------

    employee = EmployeeSerializer()

    # ------------------------------------------------------
    # DEVICE INFORMATION
    # ------------------------------------------------------

    device = DeviceSerializer()

    # ------------------------------------------------------
    # ISSUE INFORMATION
    # ------------------------------------------------------

    issue = IssueSerializer()

    # ------------------------------------------------------
    # OFFICIAL USE
    # ------------------------------------------------------

    officialUse = serializers.DictField(
        required=False,
        allow_empty=True
    )

    # ======================================================
    # CREATE DEVICE TROUBLESHOOTING REQUEST
    # ======================================================

    def create(self, validated_data):

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:

            raise serializers.ValidationError(
                "An authenticated user is required."
            )

        # --------------------------------------------------
        # REMOVE COMPANY
        # --------------------------------------------------

        company = validated_data.pop(
            "company"
        )

        # --------------------------------------------------
        # REMOVE NESTED DATA
        # --------------------------------------------------

        employee_data = validated_data.pop(
            "employee"
        )

        device_data = validated_data.pop(
            "device"
        )

        issue_data = validated_data.pop(
            "issue"
        )

        validated_data.pop(
            "currentDate",
            None
        )

        validated_data.pop(
            "officialUse",
            None
        )

        # --------------------------------------------------
        # CREATE DATABASE RECORD
        # --------------------------------------------------

        return DeviceTroubleshootingRequest.objects.create(

            # ----------------------------------------------
            # COMPANY
            # ----------------------------------------------

            company=company,

            # ----------------------------------------------
            # EMPLOYEE INFORMATION
            # ----------------------------------------------

            requester_name=employee_data["name"],

            department=employee_data["department"],

            job_title=employee_data["jobTitle"],

            employee_id=employee_data["employeeId"],

            # ----------------------------------------------
            # DEVICE INFORMATION
            # ----------------------------------------------

            asset_tag=device_data.get("assetTag") or None,

            device_type=device_data["deviceType"],

            brand_model=device_data["brandModel"],

            serial_number=device_data["serialNumber"],

            operating_system=device_data["operatingSystem"],

            # ----------------------------------------------
            # ISSUE INFORMATION
            # ----------------------------------------------

            date_reported=issue_data["dateReported"],

            reported_by=issue_data["reportedBy"],

            description=issue_data["description"],

            start_date=issue_data["startDate"],

            troubleshooting_attempted=issue_data[
                "troubleshootingAttempted"
            ],

            attempted_details=issue_data.get(
                "attemptedDetails"
            ) or None,

            # ----------------------------------------------
            # AUTHENTICATED USER
            # ----------------------------------------------

            created_by=request.user
        )

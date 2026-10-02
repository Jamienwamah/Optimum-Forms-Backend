from rest_framework import serializers

from .models import OGFSDeviceTroubleshooting


class EmployeeSerializer(serializers.Serializer):

    name = serializers.CharField(
        required=False,
        allow_blank=True
    )

    department = serializers.CharField(
        required=False,
        allow_blank=True
    )

    jobTitle = serializers.CharField(
        required=False,
        allow_blank=True
    )

    employeeId = serializers.CharField(
        required=False,
        allow_blank=True
    )


class OGFSDeviceSerializer(serializers.Serializer):

    assetTag = serializers.CharField(
        required=False,
        allow_blank=True
    )

    deviceType = serializers.CharField(
        required=True
    )

    brandModel = serializers.CharField(
        required=True
    )

    serialNumber = serializers.CharField(
        required=True
    )

    operatingSystem = serializers.CharField(
        required=True
    )


class IssueSerializer(serializers.Serializer):

    dateReported = serializers.DateField(
        required=True
    )

    reportedBy = serializers.CharField(
        required=True
    )

    description = serializers.CharField(
        required=True
    )

    startDate = serializers.DateField(
        required=True
    )

    troubleshootingAttempted = serializers.BooleanField(
        required=False,
        default=False
    )

    attemptedDetails = serializers.CharField(
        required=False,
        allow_blank=True
    )


class ConsentSerializer(serializers.Serializer):

    agreed = serializers.BooleanField(
        required=True
    )


class SignaturesSerializer(serializers.Serializer):

    employee = serializers.CharField(
        required=True
    )

    employeeDate = serializers.DateField(
        required=True
    )

    itRep = serializers.CharField(
        required=False,
        allow_blank=True
    )

    itTitle = serializers.CharField(
        required=False,
        allow_blank=True
    )

    itSignature = serializers.CharField(
        required=False,
        allow_blank=True
    )

    itDate = serializers.DateField(
        required=False,
        allow_null=True
    )


class AssessmentSerializer(serializers.Serializer):

    hardware = serializers.BooleanField(
        required=False,
        default=False
    )

    software = serializers.BooleanField(
        required=False,
        default=False
    )

    network = serializers.BooleanField(
        required=False,
        default=False
    )

    os = serializers.BooleanField(
        required=False,
        default=False
    )

    malware = serializers.BooleanField(
        required=False,
        default=False
    )

    userConfig = serializers.BooleanField(
        required=False,
        default=False
    )


class TroubleshootingSerializer(serializers.Serializer):

    hwDiag = serializers.BooleanField(
        required=False,
        default=False
    )

    osRepair = serializers.BooleanField(
        required=False,
        default=False
    )

    driverUpdates = serializers.BooleanField(
        required=False,
        default=False
    )

    swReinstall = serializers.BooleanField(
        required=False,
        default=False
    )

    malwareRemoval = serializers.BooleanField(
        required=False,
        default=False
    )

    winUpdates = serializers.BooleanField(
        required=False,
        default=False
    )

    dataBackup = serializers.BooleanField(
        required=False,
        default=False
    )

    pwdReset = serializers.BooleanField(
        required=False,
        default=False
    )

    hwReplacement = serializers.BooleanField(
        required=False,
        default=False
    )


class OfficialUseSerializer(serializers.Serializer):

    receivedBy = serializers.CharField(
        required=False,
        allow_blank=True
    )

    dateReceived = serializers.DateField(
        required=False,
        allow_null=True
    )

    assessment = AssessmentSerializer(
        required=False
    )

    assessmentOther = serializers.CharField(
        required=False,
        allow_blank=True
    )

    troubleshooting = TroubleshootingSerializer(
        required=False
    )

    partsReplaced = serializers.CharField(
        required=False,
        allow_blank=True
    )

    outcome = serializers.CharField(
        required=False,
        allow_blank=True
    )

    dateReturned = serializers.DateField(
        required=False,
        allow_null=True
    )

    returnedBy = serializers.CharField(
        required=False,
        allow_blank=True
    )

    userConfirmation = serializers.CharField(
        required=False,
        allow_blank=True
    )

    confirmationDate = serializers.DateField(
        required=False,
        allow_null=True
    )

    additionalComments = serializers.CharField(
        required=False,
        allow_blank=True
    )


class OGFSDeviceTroubleshootingSerializer(serializers.Serializer):

    # --------------------------------------------------------
    # Sent by Angular but not stored directly
    # --------------------------------------------------------

    currentDate = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True
    )

    # --------------------------------------------------------
    # Employee
    # --------------------------------------------------------

    employee = EmployeeSerializer(
        required=True
    )

    # --------------------------------------------------------
    # Device
    # --------------------------------------------------------

    device = OGFSDeviceSerializer(
        required=True
    )

    # --------------------------------------------------------
    # Issue
    # --------------------------------------------------------

    issue = IssueSerializer(
        required=True
    )

    # --------------------------------------------------------
    # Consent
    # --------------------------------------------------------

    consent = ConsentSerializer(
        required=True
    )

    # --------------------------------------------------------
    # Signatures
    # --------------------------------------------------------

    signatures = SignaturesSerializer(
        required=True
    )

    # --------------------------------------------------------
    # Official IT Use
    # --------------------------------------------------------

    officialUse = OfficialUseSerializer(
        required=False
    )

    def validate(self, attrs):

        consent_data = attrs.get(
            "consent",
            {}
        )

        if not consent_data.get("agreed", False):

            raise serializers.ValidationError(
                {
                    "consent": (
                        "You must agree to the IT diagnosis "
                        "and remediation authorization."
                    )
                }
            )

        return attrs

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
                {
                    "employee": (
                        "Microsoft Entra profile not found "
                        "for this user."
                    )
                }
            )

        # ----------------------------------------------------
        # REMOVE NESTED DATA
        # ----------------------------------------------------

        employee_data = validated_data.pop(
            "employee",
            {}
        )

        device_data = validated_data.pop(
            "device"
        )

        issue_data = validated_data.pop(
            "issue"
        )

        consent_data = validated_data.pop(
            "consent"
        )

        signatures_data = validated_data.pop(
            "signatures"
        )

        official_use_data = validated_data.pop(
            "officialUse",
            {}
        )

        # currentDate is sent by Angular
        # but is not stored directly.
        validated_data.pop(
            "currentDate",
            None
        )

        # ----------------------------------------------------
        # EMPLOYEE INFORMATION
        #
        # Name, department and job title come from Entra.
        # Employee ID comes from the Angular form.
        # ----------------------------------------------------

        employee_id = employee_data.get(
            "employeeId",
            ""
        )

        # ----------------------------------------------------
        # OFFICIAL USE DATA
        # ----------------------------------------------------

        assessment_data = official_use_data.get(
            "assessment",
            {}
        )

        troubleshooting_data = official_use_data.get(
            "troubleshooting",
            {}
        )

        # ----------------------------------------------------
        # CREATE DATABASE RECORD
        # ----------------------------------------------------

        troubleshooting = OGFSDeviceTroubleshooting.objects.create(

            # -----------------------------------------------
            # Authenticated User
            # -----------------------------------------------

            created_by=request.user,

            # -----------------------------------------------
            # Employee Information
            # -----------------------------------------------

            employee_name=profile.display_name or "",

            employee_department=profile.department or "",

            employee_job_title=profile.job_title or "",

            employee_id=employee_id,

            # -----------------------------------------------
            # Device Information
            # -----------------------------------------------

            asset_tag=device_data.get(
                "assetTag",
                ""
            ),

            device_type=device_data.get(
                "deviceType"
            ),

            brand_model=device_data.get(
                "brandModel"
            ),

            serial_number=device_data.get(
                "serialNumber"
            ),

            operating_system=device_data.get(
                "operatingSystem"
            ),

            # -----------------------------------------------
            # Issue Information
            # -----------------------------------------------

            date_reported=issue_data.get(
                "dateReported"
            ),

            reported_by=issue_data.get(
                "reportedBy"
            ),

            description=issue_data.get(
                "description"
            ),

            start_date=issue_data.get(
                "startDate"
            ),

            troubleshooting_attempted=issue_data.get(
                "troubleshootingAttempted",
                False
            ),

            attempted_details=issue_data.get(
                "attemptedDetails",
                ""
            ),

            # -----------------------------------------------
            # Consent
            # -----------------------------------------------

            consent_agreed=consent_data.get(
                "agreed",
                False
            ),

            # -----------------------------------------------
            # Employee Signature
            # -----------------------------------------------

            employee_signature=signatures_data.get(
                "employee"
            ),

            employee_signature_date=signatures_data.get(
                "employeeDate"
            ),

            # -----------------------------------------------
            # IT Representative
            # -----------------------------------------------

            it_representative=signatures_data.get(
                "itRep",
                ""
            ),

            it_title=signatures_data.get(
                "itTitle",
                ""
            ),

            it_signature=signatures_data.get(
                "itSignature",
                ""
            ),

            it_signature_date=signatures_data.get(
                "itDate"
            ),

            # -----------------------------------------------
            # Official Use
            # -----------------------------------------------

            received_by=official_use_data.get(
                "receivedBy",
                ""
            ),

            date_received=official_use_data.get(
                "dateReceived"
            ),

            # -----------------------------------------------
            # Assessment
            # -----------------------------------------------

            assessment_hardware=assessment_data.get(
                "hardware",
                False
            ),

            assessment_software=assessment_data.get(
                "software",
                False
            ),

            assessment_network=assessment_data.get(
                "network",
                False
            ),

            assessment_os=assessment_data.get(
                "os",
                False
            ),

            assessment_malware=assessment_data.get(
                "malware",
                False
            ),

            assessment_user_config=assessment_data.get(
                "userConfig",
                False
            ),

            assessment_other=official_use_data.get(
                "assessmentOther",
                ""
            ),

            # -----------------------------------------------
            # Troubleshooting Performed
            # -----------------------------------------------

            troubleshooting_hw_diag=troubleshooting_data.get(
                "hwDiag",
                False
            ),

            troubleshooting_os_repair=troubleshooting_data.get(
                "osRepair",
                False
            ),

            troubleshooting_driver_updates=troubleshooting_data.get(
                "driverUpdates",
                False
            ),

            troubleshooting_sw_reinstall=troubleshooting_data.get(
                "swReinstall",
                False
            ),

            troubleshooting_malware_removal=troubleshooting_data.get(
                "malwareRemoval",
                False
            ),

            troubleshooting_win_updates=troubleshooting_data.get(
                "winUpdates",
                False
            ),

            troubleshooting_data_backup=troubleshooting_data.get(
                "dataBackup",
                False
            ),

            troubleshooting_pwd_reset=troubleshooting_data.get(
                "pwdReset",
                False
            ),

            troubleshooting_hw_replacement=troubleshooting_data.get(
                "hwReplacement",
                False
            ),

            # -----------------------------------------------
            # Resolution
            # -----------------------------------------------

            parts_replaced=official_use_data.get(
                "partsReplaced",
                ""
            ),

            outcome=official_use_data.get(
                "outcome",
                ""
            ),

            date_returned=official_use_data.get(
                "dateReturned"
            ),

            returned_by=official_use_data.get(
                "returnedBy",
                ""
            ),

            user_confirmation=official_use_data.get(
                "userConfirmation",
                ""
            ),

            confirmation_date=official_use_data.get(
                "confirmationDate"
            ),

            additional_comments=official_use_data.get(
                "additionalComments",
                ""
            )
        )

        return troubleshooting
from rest_framework import serializers
from .models import OGCMDeviceReplacement


class EmployeeSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    department = serializers.CharField(required=False, allow_blank=True)
    jobTitle = serializers.CharField(required=False, allow_blank=True)
    employeeId = serializers.CharField(required=False, allow_blank=True)


class CurrentDeviceSerializer(serializers.Serializer):
    assetTag = serializers.CharField(required=False, allow_blank=True)
    deviceType = serializers.CharField(required=True)
    brandModel = serializers.CharField(required=True)
    serialNumber = serializers.CharField(required=True)
    reasonForReplacement = serializers.CharField(required=True)


class ReplacementDetailsSerializer(serializers.Serializer):
    requestedDeviceType = serializers.CharField(required=True)
    urgencyLevel = serializers.CharField(required=True)
    justification = serializers.CharField(required=True)
    requiredDate = serializers.DateField(required=True)


class AuthorizationSerializer(serializers.Serializer):
    agreed = serializers.BooleanField(required=True)


class SignaturesSerializer(serializers.Serializer):
    employee = serializers.CharField(required=True)
    employeeDate = serializers.DateField(required=True)
    managerName = serializers.CharField(required=False, allow_blank=True)
    managerDate = serializers.CharField(required=False, allow_blank=True)


class OGCMDeviceReplacementSerializer(serializers.Serializer):
    currentDate = serializers.CharField(required=False, allow_blank=True, write_only=True)
    employee = EmployeeSerializer(required=False)
    currentDevice = CurrentDeviceSerializer(required=True)
    replacementDetails = ReplacementDetailsSerializer(required=True)
    authorization = AuthorizationSerializer(required=True)
    signatures = SignaturesSerializer(required=True)

    def validate_authorization(self, value):
        if value.get("agreed") is not True:
            raise serializers.ValidationError("You must accept the authorization.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        profile = getattr(request.user, "entra_profile", None)

        if not profile:
            raise serializers.ValidationError({"employee": "Microsoft Entra profile not found for this user."})

        employee_data = validated_data.pop("employee", {})
        current_device_data = validated_data.pop("currentDevice")
        replacement_data = validated_data.pop("replacementDetails")
        authorization_data = validated_data.pop("authorization")
        signatures_data = validated_data.pop("signatures")
        validated_data.pop("currentDate", None)

        replacement = OGCMDeviceReplacement.objects.create(
            created_by=request.user,
            employee_name=profile.display_name or "",
            employee_id=employee_data.get("employeeId", ""),
            employee_department=profile.department or "",
            employee_job_title=profile.job_title or "",
            asset_tag=current_device_data.get("assetTag", ""),
            current_device_type=current_device_data.get("deviceType"),
            current_brand_model=current_device_data.get("brandModel"),
            current_serial_number=current_device_data.get("serialNumber"),
            reason_for_replacement=current_device_data.get("reasonForReplacement"),
            requested_device_type=replacement_data.get("requestedDeviceType"),
            urgency_level=replacement_data.get("urgencyLevel"),
            justification=replacement_data.get("justification"),
            required_date=replacement_data.get("requiredDate"),
            authorization_agreed=authorization_data.get("agreed"),
            employee_signature=signatures_data.get("employee"),
            employee_signature_date=signatures_data.get("employeeDate")
        )

        return replacement
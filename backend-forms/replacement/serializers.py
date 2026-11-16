
from rest_framework import serializers

from .models import DeviceReplacementRequest


class EmployeeSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=255)
    department = serializers.CharField(max_length=255)
    jobTitle = serializers.CharField(max_length=255)
    employeeId = serializers.CharField(max_length=100)


class CurrentDeviceSerializer(serializers.Serializer):

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

    reasonForReplacement = serializers.CharField()


class ReplacementDetailsSerializer(serializers.Serializer):

    requestedDeviceType = serializers.ChoiceField(
        choices=[
            "Laptop",
            "Desktop",
            "Mobile",
            "Peripheral"
        ]
    )

    urgencyLevel = serializers.ChoiceField(
        choices=[
            "Low",
            "Medium",
            "High"
        ]
    )

    justification = serializers.CharField()

    requiredDate = serializers.DateField()


class DeviceReplacementSerializer(serializers.Serializer):

    currentDate = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True
    )

    employee = EmployeeSerializer()

    currentDevice = CurrentDeviceSerializer()

    replacementDetails = ReplacementDetailsSerializer()

    def create(self, validated_data):

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "An authenticated user is required."
            )

        employee_data = validated_data.pop("employee")

        device_data = validated_data.pop("currentDevice")

        replacement_data = validated_data.pop(
            "replacementDetails"
        )

        validated_data.pop("currentDate", None)

        return DeviceReplacementRequest.objects.create(

            requester_name=employee_data["name"],

            department=employee_data["department"],

            job_title=employee_data["jobTitle"],

            employee_id=employee_data["employeeId"],

            asset_tag=device_data.get("assetTag") or None,

            device_type=device_data["deviceType"],

            brand_model=device_data["brandModel"],

            serial_number=device_data["serialNumber"],

            reason_for_replacement=device_data[
                "reasonForReplacement"
            ],

            requested_device_type=replacement_data[
                "requestedDeviceType"
            ],

            urgency_level=replacement_data["urgencyLevel"],

            justification=replacement_data["justification"],

            required_date=replacement_data["requiredDate"],

            created_by=request.user
        )

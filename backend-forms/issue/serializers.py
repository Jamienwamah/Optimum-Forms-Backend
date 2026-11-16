
from uuid import uuid4

from django.utils import timezone

from rest_framework import serializers

from .models import LaptopIssue


# ==========================================================
# EMPLOYEE INFORMATION SERIALIZER
# ==========================================================

class EmployeeSerializer(serializers.Serializer):

    name = serializers.CharField(
        required=True
    )

    department = serializers.CharField(
        required=True
    )

    jobTitle = serializers.CharField(
        required=True
    )

    employeeId = serializers.CharField(
        required=True
    )


# ==========================================================
# OFFICIAL LAPTOP ISSUE INFORMATION SERIALIZER
# ==========================================================

class OfficialUseSerializer(serializers.Serializer):

    laptopDetails = serializers.CharField(
        required=True
    )

    brandModel = serializers.CharField(
        required=True
    )

    serialNumber = serializers.CharField(
        required=True
    )

    accessoriesProvided = serializers.CharField(
        required=False,
        allow_blank=True
    )

    dateIssued = serializers.DateField(
        required=True
    )


# ==========================================================
# MAIN LAPTOP ISSUE SERIALIZER
# ==========================================================

class LaptopIssueSerializer(serializers.Serializer):

    # ------------------------------------------------------
    # CURRENT DATE
    # ------------------------------------------------------

    currentDate = serializers.DateField(
        required=False,
        write_only=True
    )


    # ------------------------------------------------------
    # EMPLOYEE INFORMATION
    # ------------------------------------------------------

    employee = EmployeeSerializer(
        required=True
    )


    # ------------------------------------------------------
    # OFFICIAL LAPTOP ISSUE INFORMATION
    # ------------------------------------------------------

    officialUse = OfficialUseSerializer(
        required=True
    )


    # ======================================================
    # CREATE LAPTOP ISSUE
    # ======================================================

    def create(self, validated_data):

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:

            raise serializers.ValidationError(
                {
                    "requester": (
                        "You must be authenticated to submit "
                        "a laptop issue form."
                    )
                }
            )


        # --------------------------------------------------
        # REMOVE CURRENT DATE
        # --------------------------------------------------

        validated_data.pop(
            "currentDate",
            None
        )


        # --------------------------------------------------
        # REMOVE NESTED DATA
        # --------------------------------------------------

        employee_data = validated_data.pop(
            "employee"
        )

        official_use_data = validated_data.pop(
            "officialUse"
        )


        # --------------------------------------------------
        # GENERATE DOCUMENT NUMBER
        # --------------------------------------------------

        document_no = (
            "LAPTOP-ISSUE-"
            f"{timezone.now().strftime('%Y%m%d%H%M%S')}-"
            f"{uuid4().hex[:8].upper()}"
        )


        # --------------------------------------------------
        # CREATE DATABASE RECORD
        # --------------------------------------------------

        laptop_issue = LaptopIssue.objects.create(

            # ----------------------------------------------
            # AUTHENTICATED DJANGO USER
            # ----------------------------------------------

            created_by=request.user,


            # ----------------------------------------------
            # DOCUMENT INFORMATION
            # ----------------------------------------------

            document_no=document_no,


            # ----------------------------------------------
            # EMPLOYEE INFORMATION
            # ----------------------------------------------

            requester_name=employee_data.get(
                "name"
            ),

            department=employee_data.get(
                "department"
            ),

            job_title=employee_data.get(
                "jobTitle"
            ),

            employee_id=employee_data.get(
                "employeeId"
            ),


            # ----------------------------------------------
            # LAPTOP ISSUE INFORMATION
            # ----------------------------------------------

            laptop_details=official_use_data.get(
                "laptopDetails"
            ),

            brand_model=official_use_data.get(
                "brandModel"
            ),

            serial_number=official_use_data.get(
                "serialNumber"
            ),

            accessories_provided=official_use_data.get(
                "accessoriesProvided",
                ""
            ),

            date_issued=official_use_data.get(
                "dateIssued"
            )

        )


        return laptop_issue

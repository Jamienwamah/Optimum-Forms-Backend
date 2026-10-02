from rest_framework import serializers

from .models import EnclusiaAccessRequest


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
        required=True
    )


class AccessForSerializer(serializers.Serializer):

    name = serializers.CharField(
        required=True
    )

    email = serializers.EmailField(
        required=True
    )

    def validate_email(self, value):

        value = value.strip().lower()

        if not value.endswith("@optimum-g.com"):
            raise serializers.ValidationError(
                "Only @optimum-g.com accounts are allowed."
            )

        return value


class EnclusiaAccessSerializer(serializers.Serializer):

    role = serializers.CharField(
        required=True
    )

    rolecode = serializers.CharField(
        required=True
    )

    roleDescription = serializers.CharField(
        required=True
    )

    reason = serializers.CharField(
        required=True
    )


class EnclusiaAccessRequestSerializer(serializers.Serializer):

    # ----------------------------------------------------
    # Sent by Angular but not stored directly.
    # ----------------------------------------------------

    currentDate = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True
    )

    # ----------------------------------------------------
    # Person submitting the request
    # ----------------------------------------------------

    requester = serializers.DictField(
        required=False
    )

    # ----------------------------------------------------
    # Person receiving the access
    # ----------------------------------------------------

    accessFor = AccessForSerializer(
        required=True
    )

    # ----------------------------------------------------
    # Employee information
    # ----------------------------------------------------

    employee = EmployeeSerializer(
        required=True
    )

    # ----------------------------------------------------
    # Enclusia access information
    # ----------------------------------------------------

    enclusiaAccess = EnclusiaAccessSerializer(
        required=True
    )

    def create(self, validated_data):

        request = self.context["request"]

        # ------------------------------------------------
        # GET THE LOGGED-IN USER'S ENTRA PROFILE
        # ------------------------------------------------

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

        # ------------------------------------------------
        # REMOVE NESTED DATA
        # ------------------------------------------------

        requester_data = validated_data.pop(
            "requester",
            {}
        )

        access_for_data = validated_data.pop(
            "accessFor"
        )

        employee_data = validated_data.pop(
            "employee",
            {}
        )

        enclusia_access_data = validated_data.pop(
            "enclusiaAccess"
        )

        # ------------------------------------------------
        # currentDate IS NOT STORED
        # ------------------------------------------------

        validated_data.pop(
            "currentDate",
            None
        )

        # ------------------------------------------------
        # EMPLOYEE INFORMATION
        #
        # Name, department and job title come from Entra.
        # Employee ID comes from the Angular form.
        # ------------------------------------------------

        employee_id = employee_data.get(
            "employeeId",
            ""
        )

        # ------------------------------------------------
        # REQUESTER
        #
        # We don't trust the requester name supplied
        # by Angular. The authenticated Entra profile
        # is the source of truth.
        # ------------------------------------------------

        requester_name = (
            profile.display_name
            or ""
        )

        # ------------------------------------------------
        # CREATE DATABASE RECORD
        # ------------------------------------------------

        access_request = EnclusiaAccessRequest.objects.create(

            # --------------------------------------------
            # Authenticated User
            # --------------------------------------------

            created_by=request.user,

            # --------------------------------------------
            # Requester
            # --------------------------------------------

            requester_name=requester_name,

            # --------------------------------------------
            # Person Receiving Access
            # --------------------------------------------

            access_for_name=access_for_data.get(
                "name"
            ),

            access_for_email=access_for_data.get(
                "email"
            ),

            # --------------------------------------------
            # Employee Information
            # --------------------------------------------

            employee_name=profile.display_name or "",

            employee_department=(
                profile.department or ""
            ),

            employee_job_title=(
                profile.job_title or ""
            ),

            employee_id=employee_id,

            # --------------------------------------------
            # Enclusia Access
            # --------------------------------------------

            role=enclusia_access_data.get(
                "role"
            ),

            rolecode=enclusia_access_data.get(
                "rolecode"
            ),

            role_description=(
                enclusia_access_data.get(
                    "roleDescription"
                )
            ),

            reason=enclusia_access_data.get(
                "reason"
            )
        )

        return access_request
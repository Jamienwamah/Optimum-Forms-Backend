from rest_framework import serializers
import requests

from .models import EnclusiaAccessRequest
from access_control.email import get_graph_access_token


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
        # EMPLOYEE ID
        #
        # This remains the Employee ID supplied on the
        # existing Angular form.
        # ------------------------------------------------

        employee_id = employee_data.get(
            "employeeId",
            ""
        )

        # ------------------------------------------------
        # REQUESTER
        #
        # We do not trust the requester information
        # supplied by Angular.
        #
        # The authenticated Entra profile remains the
        # source of truth.
        # ------------------------------------------------

        requester_name = (
            profile.display_name
            or ""
        )

        requester_email = (
            getattr(
                profile,
                "email",
                None
            )
            or getattr(
                profile,
                "user_principal_name",
                None
            )
            or getattr(
                request.user,
                "email",
                ""
            )
            or ""
        )

        # ------------------------------------------------
        # VERIFY ACCESS-FOR EMPLOYEE IN MICROSOFT ENTRA
        # ------------------------------------------------
        #
        # The person creating the request and the person
        # receiving the access can be different people.
        #
        # The email entered in accessFor.email is checked
        # directly against Microsoft Entra.
        # ------------------------------------------------

        access_for_email = (
            access_for_data
            .get("email", "")
            .strip()
            .lower()
        )

        try:

            graph_token = get_graph_access_token()

        except Exception as error:

            raise serializers.ValidationError(
                {
                    "accessFor": (
                        "Unable to verify the employee "
                        "against Microsoft Entra ID."
                    )
                }
            ) from error

        # ------------------------------------------------
        # MICROSOFT GRAPH USER LOOKUP
        #
        # Search by both mail and userPrincipalName.
        # This keeps the submitted accessFor email as the
        # lookup value without changing the existing form.
        # ------------------------------------------------

        safe_email = access_for_email.replace(
            "'",
            "''"
        )

        graph_url = (
            "https://graph.microsoft.com/v1.0/users"
        )

        try:

            graph_response = requests.get(

                graph_url,

                headers={
                    "Authorization": (
                        f"Bearer {graph_token}"
                    )
                },

                params={
                    "$filter": (
                        f"mail eq '{safe_email}' "
                        f"or userPrincipalName eq "
                        f"'{safe_email}'"
                    ),
                    "$select": (
                        "id,"
                        "displayName,"
                        "mail,"
                        "userPrincipalName,"
                        "department,"
                        "jobTitle,"
                        "employeeId"
                    ),
                    "$top": "1"
                },

                timeout=15

            )

        except requests.RequestException as error:

            raise serializers.ValidationError(
                {
                    "accessFor": (
                        "Unable to contact Microsoft "
                        "Entra ID to verify the employee."
                    )
                }
            ) from error

        # ------------------------------------------------
        # GRAPH AUTHORIZATION ERROR
        # ------------------------------------------------

        # if graph_response.status_code in (
        #     401,
        #     403
        # ):

        #     raise serializers.ValidationError(
        #         {
        #             "accessFor": (
        #                 "The system could not verify the "
        #                 "employee because Microsoft Entra "
        #                 "authorization is unavailable."
        #             )
        #         }
        #     )

        if graph_response.status_code in (
            401,
            403
        ):
            raise serializers.ValidationError(
                {
                    "accessFor": (
                        f"Microsoft Graph returned "
                        f"HTTP {graph_response.status_code}: "
                        f"{graph_response.text}"
                    )
                }
            )

        # ------------------------------------------------
        # OTHER GRAPH ERROR
        # ------------------------------------------------

        if not graph_response.ok:

            raise serializers.ValidationError(
                {
                    "accessFor": (
                        "Unable to verify the employee "
                        "against Microsoft Entra ID."
                    )
                }
            )

        # ------------------------------------------------
        # GET GRAPH USER RESULT
        #
        # A filtered /users request returns HTTP 200 even
        # when no matching user exists.
        # ------------------------------------------------

        graph_data = graph_response.json()

        graph_users = graph_data.get(
            "value",
            []
        )

        # ------------------------------------------------
        # EMPLOYEE DOES NOT EXIST
        # ------------------------------------------------

        if not graph_users:

            raise serializers.ValidationError(
                {
                    "accessFor": {
                        "email": (
                            "The supplied Microsoft account "
                            "does not exist in the Optimum "
                            "Global Entra directory."
                        )
                    }
                }
            )

        access_for_profile = graph_users[0]

        # ------------------------------------------------
        # VERIFY THAT GRAPH ACTUALLY RETURNED A USER
        # ------------------------------------------------

        access_for_object_id = (
            access_for_profile.get("id")
        )

        if not access_for_object_id:

            raise serializers.ValidationError(
                {
                    "accessFor": {
                        "email": (
                            "The supplied email could not "
                            "be matched to a Microsoft "
                            "Entra user."
                        )
                    }
                }
            )

        # ------------------------------------------------
        # GET AUTHORITATIVE ENTRA INFORMATION
        # ------------------------------------------------

        access_for_name = (
            access_for_profile.get(
                "displayName"
            )
            or access_for_data.get(
                "name",
                ""
            )
        )

        access_for_mail = (
            access_for_profile.get(
                "mail"
            )
            or access_for_profile.get(
                "userPrincipalName"
            )
            or access_for_email
        )

        access_for_department = (
            access_for_profile.get(
                "department"
            )
            or ""
        ).strip()

        access_for_job_title = (
            access_for_profile.get(
                "jobTitle"
            )
            or ""
        )

        access_for_employee_id = (
            access_for_profile.get(
                "employeeId"
            )
            or ""
        )

        # ------------------------------------------------
        # DEPARTMENT IS REQUIRED FOR APPROVAL ROUTING
        # ------------------------------------------------

        if not access_for_department:

            raise serializers.ValidationError(
                {
                    "accessFor": {
                        "email": (
                            "The employee exists in "
                            "Microsoft Entra ID, but no "
                            "department is assigned to "
                            "the employee. Approval "
                            "routing cannot be determined."
                        )
                    }
                }
            )

        # ------------------------------------------------
        # CREATE DATABASE RECORD
        # ------------------------------------------------
        #
        # IMPORTANT:
        #
        # employee_* fields continue to represent the
        # PERSON CREATING THE REQUEST.
        #
        # access_for_* fields represent the PERSON
        # RECEIVING THE ACCESS.
        # ------------------------------------------------

        access_request = (
            EnclusiaAccessRequest.objects.create(

                # ----------------------------------------
                # Authenticated User
                # ----------------------------------------

                created_by=request.user,

                # ----------------------------------------
                # Requester
                # ----------------------------------------

                requester_name=requester_name,

                # ----------------------------------------
                # Person Receiving Access
                # ----------------------------------------

                access_for_name=access_for_name,

                access_for_email=access_for_mail,

                # ----------------------------------------
                # Requester's Employee Information
                # ----------------------------------------

                employee_name=(
                    profile.display_name
                    or ""
                ),

                employee_department=(
                    profile.department
                    or ""
                ),

                employee_job_title=(
                    profile.job_title
                    or ""
                ),

                employee_id=employee_id,

                # ----------------------------------------
                # Enclusia Access
                # ----------------------------------------

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
        )

        # ------------------------------------------------
        # KEEP VERIFIED ENTRA DATA AVAILABLE TO THE VIEW
        # ------------------------------------------------
        #
        # These are not database fields.
        # They are temporary attributes used by the
        # view when creating the ApprovalRequest.
        # ------------------------------------------------

        access_request.verified_access_for = {
            "id": access_for_object_id,
            "name": access_for_name,
            "email": access_for_mail,
            "department": access_for_department,
            "jobTitle": access_for_job_title,
            "employeeId": access_for_employee_id
        }

        access_request.verified_requester = {
            "name": requester_name,
            "email": requester_email,
            "department": (
                profile.department
                or ""
            ),
            "jobTitle": (
                profile.job_title
                or ""
            ),
            "employeeId": (
                profile.employee_id
                or employee_id
            )
        }

        return access_request
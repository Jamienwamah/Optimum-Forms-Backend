
from rest_framework import serializers
import requests

from .models import EnclusiaAccessRequest
from access_control.graph import get_graph_access_token


# ==========================================================
# EMPLOYEE INFORMATION SERIALIZER
# ==========================================================

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
        required=True,
        allow_blank=False
    )


# ==========================================================
# REQUESTER SERIALIZER
# ==========================================================

class RequesterSerializer(serializers.Serializer):

    name = serializers.CharField(
        required=False,
        allow_blank=True
    )


# ==========================================================
# ACCESS FOR USER SERIALIZER
# ==========================================================

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


# ==========================================================
# ENCLUSIA ACCESS SERIALIZER
# ==========================================================

class EnclusiaAccessSerializer(serializers.Serializer):

    # expirationType = serializers.ChoiceField(
    #     choices=[
    #         choice[0]
    #         for choice in EnclusiaAccessRequest.EXPIRATION_TYPE_CHOICES
    #     ],
    #     required=True
    # )

    accessRequired = serializers.ChoiceField(
        choices=[
            choice[0]
            for choice in EnclusiaAccessRequest.ACCESS_REQUIRED_CHOICES
        ],
        required=True
    )

    justification = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True
    )

    def validate_justification(self, value):

        if len(value.strip()) < 10:

            raise serializers.ValidationError(
                "Please provide a more detailed justification."
            )

        return value.strip()


# ==========================================================
# MAIN ENCLUSIA ACCESS REQUEST SERIALIZER
# ==========================================================

class EnclusiaAccessRequestSerializer(serializers.Serializer):

    # ------------------------------------------------------
    # CURRENT DATE
    # ------------------------------------------------------

    currentDate = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True
    )


    # ------------------------------------------------------
    # PERSON SUBMITTING THE REQUEST
    # ------------------------------------------------------

    requester = RequesterSerializer(
        required=False
    )


    # ------------------------------------------------------
    # PERSON RECEIVING THE ACCESS
    # ------------------------------------------------------

    accessFor = AccessForSerializer(
        required=True
    )


    # ------------------------------------------------------
    # EMPLOYEE INFORMATION
    # ------------------------------------------------------

    employee = EmployeeSerializer(
        required=True
    )


    # ------------------------------------------------------
    # ENCLUSIA ACCESS INFORMATION
    # ------------------------------------------------------

    enclusiaAccess = EnclusiaAccessSerializer(
        required=True
    )


    # ======================================================
    # CREATE ACCESS REQUEST
    # ======================================================

    def create(self, validated_data):

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:

            raise serializers.ValidationError(
                {
                    "requester": (
                        "You must be authenticated to submit "
                        "an Enclusia access request."
                    )
                }
            )


        # --------------------------------------------------
        # GET AUTHENTICATED USER'S ENTRA PROFILE
        # --------------------------------------------------

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


        # --------------------------------------------------
        # REMOVE NESTED DATA
        # --------------------------------------------------

        validated_data.pop(
            "requester",
            None
        )

        validated_data.pop(
            "currentDate",
            None
        )

        access_for_data = validated_data.pop(
            "accessFor"
        )

        employee_data = validated_data.pop(
            "employee"
        )

        enclusia_access_data = validated_data.pop(
            "enclusiaAccess"
        )


        # --------------------------------------------------
        # AUTHENTICATED REQUESTER INFORMATION
        #
        # The authenticated Entra profile is the source
        # of truth, not the name supplied by Angular.
        # --------------------------------------------------

        requester_name = (
            getattr(profile, "display_name", "")
            or ""
        ).strip()

        requester_email = (
            getattr(profile, "email", None)
            or getattr(profile, "user_principal_name", None)
            or getattr(request.user, "email", "")
            or ""
        ).strip().lower()


        if not requester_name:

            raise serializers.ValidationError(
                {
                    "requester": (
                        "Your Microsoft Entra display name "
                        "could not be retrieved."
                    )
                }
            )


        # --------------------------------------------------
        # REQUESTER EMPLOYEE INFORMATION
        # --------------------------------------------------

        requester_department = (
            getattr(profile, "department", "")
            or ""
        ).strip()

        requester_job_title = (
            getattr(profile, "job_title", "")
            or ""
        ).strip()


        # --------------------------------------------------
        # EMPLOYEE ID
        #
        # Employee ID is supplied through the existing
        # Angular form because it may not be available
        # in the Entra profile.
        # --------------------------------------------------

        employee_id = (
            employee_data.get("employeeId", "")
            or ""
        ).strip()

        if not employee_id:

            raise serializers.ValidationError(
                {
                    "employee": {
                        "employeeId": (
                            "Employee ID is required."
                        )
                    }
                }
            )


        # --------------------------------------------------
        # VERIFY ACCESS-FOR EMPLOYEE IN MICROSOFT ENTRA
        #
        # The requester and the person receiving access
        # may be different employees.
        # --------------------------------------------------

        access_for_email = (
            access_for_data.get("email", "")
            .strip()
            .lower()
        )


        # --------------------------------------------------
        # GET MICROSOFT GRAPH ACCESS TOKEN
        # --------------------------------------------------

        try:

            graph_token = get_graph_access_token()

        except Exception as error:

            raise serializers.ValidationError(
                {
                    "accessFor": (
                        "Unable to obtain Microsoft Graph "
                        "authorization to verify the employee."
                    )
                }
            ) from error


        # --------------------------------------------------
        # MICROSOFT GRAPH USER LOOKUP
        # --------------------------------------------------

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
                        f"or userPrincipalName eq '{safe_email}'"
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
                        "Unable to contact Microsoft Entra ID "
                        "to verify the employee."
                    )
                }
            ) from error


        # --------------------------------------------------
        # GRAPH AUTHORIZATION ERROR
        # --------------------------------------------------

        if graph_response.status_code in (401, 403):

            raise serializers.ValidationError(
                {
                    "accessFor": (
                        "Microsoft Graph authorization failed. "
                        "Please contact IT Support."
                    )
                }
            )


        # --------------------------------------------------
        # OTHER GRAPH ERRORS
        # --------------------------------------------------

        if not graph_response.ok:

            raise serializers.ValidationError(
                {
                    "accessFor": (
                        "Unable to verify the employee "
                        "against Microsoft Entra ID."
                    )
                }
            )


        # --------------------------------------------------
        # GET GRAPH USER RESULT
        # --------------------------------------------------

        try:

            graph_data = graph_response.json()

        except ValueError as error:

            raise serializers.ValidationError(
                {
                    "accessFor": (
                        "Microsoft Entra returned an "
                        "invalid response."
                    )
                }
            ) from error


        graph_users = graph_data.get(
            "value",
            []
        )


        # --------------------------------------------------
        # EMPLOYEE DOES NOT EXIST
        # --------------------------------------------------

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


        # --------------------------------------------------
        # VERIFY GRAPH RETURNED A USER IDENTITY
        # --------------------------------------------------

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


        # --------------------------------------------------
        # GET AUTHORITATIVE ENTRA INFORMATION
        # --------------------------------------------------

        access_for_name = (
            access_for_profile.get("displayName")
            or access_for_data.get("name", "")
        ).strip()

        access_for_mail = (
            access_for_profile.get("mail")
            or access_for_profile.get("userPrincipalName")
            or access_for_email
        ).strip().lower()

        access_for_department = (
            access_for_profile.get("department")
            or ""
        ).strip()

        access_for_job_title = (
            access_for_profile.get("jobTitle")
            or ""
        ).strip()

        access_for_employee_id = (
            access_for_profile.get("employeeId")
            or ""
        ).strip()


        # --------------------------------------------------
        # VERIFY THE RETURNED ENTRA EMAIL
        # --------------------------------------------------

        if not access_for_mail.endswith("@optimum-g.com"):

            raise serializers.ValidationError(
                {
                    "accessFor": {
                        "email": (
                            "The matched Entra account does "
                            "not have an approved Optimum "
                            "Global email address."
                        )
                    }
                }
            )


        # --------------------------------------------------
        # DEPARTMENT IS REQUIRED FOR APPROVAL ROUTING
        # --------------------------------------------------

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


        # --------------------------------------------------
        # CREATE DATABASE RECORD
        #
        # employee_* fields represent the PERSON CREATING
        # THE REQUEST.
        #
        # access_for_* fields represent the PERSON
        # RECEIVING THE ACCESS.
        # --------------------------------------------------

        access_request = EnclusiaAccessRequest.objects.create(

            # ----------------------------------------------
            # AUTHENTICATED DJANGO USER
            # ----------------------------------------------

            created_by=request.user,


            # ----------------------------------------------
            # REQUESTER
            # ----------------------------------------------

            requester_name=requester_name,


            # ----------------------------------------------
            # PERSON RECEIVING ACCESS
            # ----------------------------------------------

            access_for_name=access_for_name,

            access_for_email=access_for_mail,


            # ----------------------------------------------
            # REQUESTER EMPLOYEE INFORMATION
            # ----------------------------------------------

            employee_name=requester_name,

            employee_department=requester_department,

            employee_job_title=requester_job_title,

            employee_id=employee_id,


            # ----------------------------------------------
            # ENCLUSIA ACCESS INFORMATION
            # ----------------------------------------------

            # expiration_type=(
            #     enclusia_access_data.get(
            #         "expirationType"
            #     )
            # ),

            access_required=(
                enclusia_access_data.get(
                    "accessRequired"
                )
            ),

            justification=(
                enclusia_access_data.get(
                    "justification"
                )
            )

        )


        # --------------------------------------------------
        # KEEP VERIFIED ENTRA DATA AVAILABLE TO THE VIEW
        #
        # These are temporary attributes, not database
        # fields. Your view can use them when creating
        # the ApprovalRequest.
        # --------------------------------------------------

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

            "department": requester_department,

            "jobTitle": requester_job_title,

            "employeeId": (
                getattr(profile, "employee_id", None)
                or employee_id
            )

        }


        return access_request

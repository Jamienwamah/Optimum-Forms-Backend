from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from access_control.department_routing import get_approval_department
from access_control.models import ApprovalRequest

from .serializers import EnclusiaAccessRequestSerializer


class EnclusiaAccessRequestCreateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        # ========================================================
        # VALIDATE AND CREATE ENCLUSIA ACCESS REQUEST
        # ========================================================

        serializer = EnclusiaAccessRequestSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        if not serializer.is_valid():

            return Response(
                {
                    "message": "Validation failed.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ========================================================
        # SAVE ENCLUSIA REQUEST
        #
        # The serializer has already verified the
        # accessFor email against Microsoft Entra.
        # ========================================================

        access_request = serializer.save()

        # ========================================================
        # GET VERIFIED ACCESS-FOR EMPLOYEE
        # ========================================================

        verified_access_for = getattr(
            access_request,
            "verified_access_for",
            None
        )

        if not verified_access_for:

            return Response(
                {
                    "message": (
                        "Unable to verify the employee "
                        "receiving the requested access."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ========================================================
        # GET VERIFIED REQUESTER
        # ========================================================

        verified_requester = getattr(
            access_request,
            "verified_requester",
            None
        )

        if not verified_requester:

            return Response(
                {
                    "message": (
                        "Unable to determine the person "
                        "creating this request."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ========================================================
        # DETERMINE APPROVAL DEPARTMENT
        #
        # IMPORTANT:
        #
        # The approval department now comes from the
        # ACCESS-FOR EMPLOYEE'S Microsoft Entra department.
        #
        # It does NOT come from the requester's department.
        # It does NOT come from the Angular payload.
        # ========================================================

        employee_department = (
            verified_access_for
            .get("department", "")
            .strip()
        )

        if not employee_department:

            return Response(
                {
                    "message": (
                        "Unable to determine the department "
                        "of the employee receiving access."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            approval = get_approval_department(
                "OST-ENCLUSIA-ACCESS",
                employee_department
            )

        except ValueError as error:

            return Response(
                {
                    "message": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ========================================================
        # BUILD VERIFIED SUBMISSION DATA
        #
        # This allows the Approval Dashboard to reveal:
        #
        # 1. Person receiving access
        # 2. Person creating the request
        #
        # while keeping the existing submission data.
        # ========================================================

        submission_data = dict(
            request.data
        )

        submission_data["verifiedAccessFor"] = {
            "name": verified_access_for.get(
                "name",
                ""
            ),

            "email": verified_access_for.get(
                "email",
                ""
            ),

            "department": verified_access_for.get(
                "department",
                ""
            ),

            "jobTitle": verified_access_for.get(
                "jobTitle",
                ""
            ),

            "employeeId": verified_access_for.get(
                "employeeId",
                ""
            ),

            "entraObjectId": verified_access_for.get(
                "id",
                ""
            )
        }

        submission_data["verifiedRequester"] = {
            "name": verified_requester.get(
                "name",
                ""
            ),

            "email": verified_requester.get(
                "email",
                ""
            ),

            "department": verified_requester.get(
                "department",
                ""
            ),

            "jobTitle": verified_requester.get(
                "jobTitle",
                ""
            ),

            "employeeId": verified_requester.get(
                "employeeId",
                ""
            )
        }

        # ========================================================
        # CREATE APPROVAL REQUEST
        # ========================================================

        approval_request = ApprovalRequest.objects.create(

            # -----------------------------------------------
            # Person creating the request
            # -----------------------------------------------

            user=request.user,

            # -----------------------------------------------
            # Form
            # -----------------------------------------------

            form_code="OST-ENCLUSIA-ACCESS",

            # -----------------------------------------------
            # Department receiving the approval
            #
            # This is based on the ACCESS-FOR employee.
            # -----------------------------------------------

            department=approval["department"],

            department_email=approval["email"],

            # -----------------------------------------------
            # Reason
            # -----------------------------------------------

            reason=(
                request.data
                .get("enclusiaAccess", {})
                .get("reason", "")
            ),

            # -----------------------------------------------
            # Verified submission information
            # -----------------------------------------------

            submission_data=submission_data,
        )

        # ========================================================
        # RESPONSE
        # ========================================================

        return Response(
            {
                "message": (
                    "Enclusia Cloud Platform "
                    "access request submitted successfully."
                ),

                "id": access_request.id,

                "approval_request_id":
                    approval_request.id,

                "approval_department":
                    approval_request.department,

                "approval_status":
                    approval_request.status,

                "access_for": {
                    "name": verified_access_for.get(
                        "name",
                        ""
                    ),

                    "email": verified_access_for.get(
                        "email",
                        ""
                    ),

                    "department": verified_access_for.get(
                        "department",
                        ""
                    )
                },

                "requester": {
                    "name": verified_requester.get(
                        "name",
                        ""
                    ),

                    "email": verified_requester.get(
                        "email",
                        ""
                    )
                },

                "request_date":
                    access_request.request_date,
            },

            status=status.HTTP_201_CREATED
        )
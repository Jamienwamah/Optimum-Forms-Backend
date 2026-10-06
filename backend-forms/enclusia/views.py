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
        # ========================================================

        access_request = serializer.save()

        # ========================================================
        # DETERMINE APPROVAL DEPARTMENT
        #
        # Enclusia requests are routed to the employee's
        # own department.
        # ========================================================

        employee_department = (
            request.data
            .get("employee", {})
            .get("department", "")
            .strip()
        )

        if not employee_department:

            return Response(
                {
                    "message": (
                        "Unable to determine the employee's "
                        "department."
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
        # CREATE APPROVAL REQUEST
        # ========================================================

        approval_request = ApprovalRequest.objects.create(

            user=request.user,

            form_code="OST-ENCLUSIA-ACCESS",

            department=approval["department"],

            department_email=approval["email"],

            reason=(
                request.data
                .get("enclusiaAccess", {})
                .get("reason", "")
            ),

            submission_data=request.data,

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

                "request_date":
                    access_request.request_date,
            },

            status=status.HTTP_201_CREATED
        )
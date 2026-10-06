from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from access_control.services import user_has_form_access

from entraprofile.models import EntraProfile
from .serializers import DeviceTroubleshootingSerializer


# ============================================================
# GET EMPLOYEE INFORMATION
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_troubleshoot_employee(request):

    # ========================================================
    # ACCESS CONTROL
    # ========================================================

    if not user_has_form_access(
        request.user,
        "OGCM-TROUBLESHOOTING"
    ):
        return Response(
            {
                "status": "error",
                "message": (
                    "You do not have approval to "
                    "access this form."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    profile = getattr(
        request.user,
        "entra_profile",
        None
    )

    if not profile:
        return Response(
            {
                "status": "error",
                "message": (
                    "Microsoft Entra profile "
                    "not found for this user."
                )
            },
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(
        {
            "status": "success",
            "employee": {
                "name": profile.display_name,
                "employeeId": profile.employee_id,
                "department": profile.department,
                "jobTitle": profile.job_title
            }
        },
        status=status.HTTP_200_OK
    )


# ============================================================
# SUBMIT DEVICE TROUBLESHOOTING FORM
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_device_troubleshoot(request):

    # ========================================================
    # ACCESS CONTROL
    # ========================================================

    if not user_has_form_access(
        request.user,
        "OGCM-TROUBLESHOOTING"
    ):
        return Response(
            {
                "status": "error",
                "message": (
                    "You do not have approval to "
                    "access this form."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = DeviceTroubleshootingSerializer(
        data=request.data,
        context={
            "request": request
        }
    )

    if not serializer.is_valid():

        return Response(
            {
                "status": "error",
                "message": (
                    "Unable to submit "
                    "device troubleshooting request."
                ),
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    troubleshooting = serializer.save()

    return Response(
        {
            "status": "success",
            "message": (
                "Device troubleshooting request "
                "submitted successfully."
            ),
            "id": troubleshooting.id
        },
        status=status.HTTP_201_CREATED
    )
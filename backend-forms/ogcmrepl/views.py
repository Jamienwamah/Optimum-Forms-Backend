from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from access_control.department_routing import get_approval_department
from access_control.models import ApprovalRequest

from .serializers import OGCMDeviceReplacementSerializer


FORM_ACCESS_CODE = "OGCM-REPLACEMENT"


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_replacement_employee(request):

    profile = getattr(request.user, "entra_profile", None)

    if not profile:
        return Response(
            {
                "status": "error",
                "message": "Microsoft Entra profile not found for this user."
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_device_replacement(request):

    serializer = OGCMDeviceReplacementSerializer(
        data=request.data,
        context={"request": request}
    )

    if not serializer.is_valid():

        print("REPLACEMENT SERIALIZER ERRORS:")
        print(serializer.errors)

        return Response(
            {
                "status": "error",
                "message": "Unable to submit device replacement request.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    replacement = serializer.save()

    # ========================================================
    # DEVICE REQUESTS ARE ALWAYS ROUTED TO IT SUPPORT
    # ========================================================

    try:

        approval = get_approval_department(
            FORM_ACCESS_CODE,
            ""
        )

    except ValueError as error:

        replacement.delete()

        return Response(
            {
                "status": "error",
                "message": str(error)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ========================================================
    # CREATE APPROVAL REQUEST
    # ========================================================

    approval_request = ApprovalRequest.objects.create(
        user=request.user,
        form_code=FORM_ACCESS_CODE,
        department=approval["department"],
        department_email=approval["email"],
        reason=request.data.get("reason", ""),
        submission_data=request.data
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return Response(
        {
            "status": "success",
            "message": "Device replacement request submitted successfully.",
            "id": replacement.id,
            "approval_request_id": approval_request.id,
            "approval_department": approval_request.department,
            "approval_status": approval_request.status
        },
        status=status.HTTP_201_CREATED
    )
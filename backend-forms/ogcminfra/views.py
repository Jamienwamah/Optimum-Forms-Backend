# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# from entraprofile.models import EntraProfile
# from .serializers import OGCMInfrastructureReceiptSerializer


# # ============================================================
# # GET EMPLOYEE INFORMATION
# # ============================================================

# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def get_infrastructure_employee(request):
#     profile = getattr(request.user, "entra_profile", None)

#     if not profile:
#         return Response({"status": "error", "message": "Microsoft Entra profile not found for this user."}, status=status.HTTP_404_NOT_FOUND)

#     return Response({"status": "success", "employee": {"name": profile.display_name, "employeeId": profile.employee_id, "department": profile.department, "jobTitle": profile.job_title}}, status=status.HTTP_200_OK)


# # ============================================================
# # SUBMIT DEVICE REPLACEMENT FORM
# # ============================================================

# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def create_device_infrastructure(request):
#     serializer = OGCMInfrastructureReceiptSerializer(data=request.data, context={"request": request})

#     if not serializer.is_valid():
#         return Response({"status": "error", "message": "Unable to submit device infrastructure request.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#     infrastructure = serializer.save()

#     return Response({"status": "success", "message": "Device infrastructure request submitted successfully.", "id": infrastructure.id}, status=status.HTTP_201_CREATED)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import OGCMInfrastructureReceiptSerializer


# ============================================================
# GET EMPLOYEE INFORMATION
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_infrastructure_employee(request):

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


# ============================================================
# SUBMIT INFRASTRUCTURE RECEIPT
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_device_infrastructure(request):

    serializer = OGCMInfrastructureReceiptSerializer(
        data=request.data,
        context={"request": request}
    )

    if not serializer.is_valid():
        print("INFRASTRUCTURE SERIALIZER ERRORS:")
        print(serializer.errors)

        return Response(
            {
                "status": "error",
                "message": "Unable to submit infrastructure request.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    infrastructure = serializer.save()

    return Response(
        {
            "status": "success",
            "message": "Infrastructure request submitted successfully.",
            "id": infrastructure.id
        },
        status=status.HTTP_201_CREATED
    )
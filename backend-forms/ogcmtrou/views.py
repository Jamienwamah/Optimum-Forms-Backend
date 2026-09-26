from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from entraprofile.models import EntraProfile
from .serializers import OGCMDeviceTroubleshootSerializer


# ============================================================
# GET EMPLOYEE INFORMATION
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_troubleshoot_employee(request):
    profile = getattr(request.user, "entra_profile", None)

    if not profile:
        return Response({"status": "error", "message": "Microsoft Entra profile not found for this user."}, status=status.HTTP_404_NOT_FOUND)

    return Response({"status": "success", "employee": {"name": profile.display_name, "employeeId": profile.employee_id, "department": profile.department, "jobTitle": profile.job_title}}, status=status.HTTP_200_OK)


# ============================================================
# SUBMIT DEVICE REPLACEMENT FORM
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_device_troubleshoot(request):
    serializer = OGCMDeviceTroubleshootSerializer(data=request.data, context={"request": request})

    if not serializer.is_valid():
        return Response({"status": "error", "message": "Unable to submit device replacement request.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    replacement = serializer.save()

    return Response({"status": "success", "message": "Device replacement request submitted successfully.", "id": replacement.id}, status=status.HTTP_201_CREATED)

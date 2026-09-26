from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import EntraProfile


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_profile(request):

    try:

        profile = EntraProfile.objects.get(
            user=request.user
        )

        return Response(
            {
                "status": "success",

                "profile": {
                    "name": profile.display_name,
                    "givenName": profile.given_name,
                    "familyName": profile.family_name,
                    "employeeId": profile.employee_id,
                    "department": profile.department,
                    "jobTitle": profile.job_title,
                    "entraObjectId": profile.entra_object_id,
                    "tenantId": profile.tenant_id
                }
            },
            status=status.HTTP_200_OK
        )

    except EntraProfile.DoesNotExist:

        return Response(
            {
                "status": "error",
                "message": "Entra profile not found for the authenticated user."
            },
            status=status.HTTP_404_NOT_FOUND
        )
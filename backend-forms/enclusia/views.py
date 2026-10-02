from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import EnclusiaAccessRequestSerializer


class EnclusiaAccessRequestCreateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        serializer = EnclusiaAccessRequestSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        if serializer.is_valid():

            access_request = serializer.save()

            return Response(
                {
                    "message": (
                        "Enclusia Cloud Platform "
                        "access request submitted successfully."
                    ),
                    "id": access_request.id,
                    "status": access_request.status,
                    "request_date": access_request.request_date,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "message": "Validation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )
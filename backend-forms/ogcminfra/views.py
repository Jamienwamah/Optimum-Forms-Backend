from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import OGCMInfrastructureReceipt
from .serializers import OGCMInfrastructureReceiptSerializer

class OGCMInfrastructureReceiptViewSet(viewsets.ModelViewSet):
    queryset = OGCMInfrastructureReceipt.objects.all()
    serializer_class = OGCMInfrastructureReceiptSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        full_name = user.get_full_name() or user.username or user.email
        serializer.save(created_by=user, user_name=full_name, user_email=user.email, user_department=getattr(user, 'department', ''), user_job_title=getattr(user, 'job_title', ''), user_company=getattr(user, 'company', ''),
                         procured_by=full_name, inspected_by=full_name)
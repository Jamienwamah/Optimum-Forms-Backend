from rest_framework.routers import DefaultRouter
from .views import OGCMInfrastructureReceiptViewSet

router = DefaultRouter()
router.register(r'ogcm/infrastructure-receipts', OGCMInfrastructureReceiptViewSet, basename='ogcm-infrastructure-receipt')

urlpatterns = router.urls
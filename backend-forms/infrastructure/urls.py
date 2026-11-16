from django.urls import path

from .views import InfrastructureReceiptCreateView


urlpatterns = [

    path(
        "infrastructure/",
        InfrastructureReceiptCreateView.as_view(),
        name="infrastructure-receipt-create"
    ),

]
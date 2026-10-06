from django.urls import path
from .views import ApprovalRequestListView, ApprovalRequestStatsView, ApproveApprovalRequestView, EmailApprovalDecisionView, MyApprovalRequestsView, RejectApprovalRequestView, SubmitApprovalRequestView

urlpatterns = [
    path("submit/", SubmitApprovalRequestView.as_view(), name="submit-approval-request"),
    path("mine/", MyApprovalRequestsView.as_view(), name="my-approval-requests"),
    path("admin/requests/", ApprovalRequestListView.as_view(), name="approval-requests"),
    path("admin/stats/", ApprovalRequestStatsView.as_view(), name="approval-stats"),
    path("admin/requests/<int:pk>/approve/", ApproveApprovalRequestView.as_view(), name="approve-approval-request"),
    path("admin/requests/<int:pk>/reject/", RejectApprovalRequestView.as_view(), name="reject-approval-request"),
    path("email-decision/<str:decision>/<str:token>/", EmailApprovalDecisionView.as_view(), name="approval-decision"),
]
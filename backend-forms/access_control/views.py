from django.core.signing import BadSignature, SignatureExpired, loads
from django.http import HttpResponse
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .department_routing import get_approval_department
from .email import send_approval_request_email
from .models import ApprovalRequest
from .permissions import IsApprovalAdministrator
from .serializers import ApprovalRequestSerializer


class SubmitApprovalRequestView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        form_code = request.data.get("form_code")

        if not form_code:
            return Response(
                {
                    "detail": "form_code is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = request.data.get(
            "reason",
            "",
        )

        submission_data = request.data.get(
            "submission_data",
            {},
        )

        employee_department = ""

        employee = request.data.get(
            "employee",
            {},
        )

        if isinstance(employee, dict):
            employee_department = str(
                employee.get(
                    "department",
                    "",
                )
            ).strip()

        if not employee_department:
            employee_department = str(
                getattr(
                    request.user,
                    "department",
                    "",
                )
            ).strip()

        try:

            routing = get_approval_department(
                form_code,
                employee_department,
            )

        except ValueError as error:

            return Response(
                {
                    "detail": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing = ApprovalRequest.objects.filter(
            user=request.user,
            form_code=form_code,
            status=ApprovalRequest.STATUS_PENDING,
        ).first()

        if existing:

            return Response(
                {
                    "detail": (
                        "A request for this form "
                        "is already pending approval."
                    ),
                    "id": existing.id,
                    "form_code": existing.form_code,
                    "department": existing.department,
                    "status": existing.status,
                    "submitted_at": existing.submitted_at,
                },
                status=status.HTTP_200_OK,
            )

        approval_request = ApprovalRequest.objects.create(
            user=request.user,
            form_code=form_code,
            department=routing["department"],
            department_email=routing["email"],
            reason=reason,
            submission_data=submission_data,
            status=ApprovalRequest.STATUS_PENDING,
        )

        try:

            send_approval_request_email(
                approval_request
            )

        except Exception as error:

            approval_request.delete()

            return Response(
                {
                    "detail": (
                        "The request could not be submitted "
                        "because the approval email could not "
                        "be sent."
                    ),
                    "error": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "id": approval_request.id,
                "form_code": approval_request.form_code,
                "department": approval_request.department,
                "status": approval_request.status,
                "submitted_at": approval_request.submitted_at,
            },
            status=status.HTTP_201_CREATED,
        )


class MyApprovalRequestsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        requests = (
            ApprovalRequest.objects
            .filter(
                user=request.user
            )
            .order_by(
                "-submitted_at"
            )
        )

        data = []

        for approval_request in requests:

            data.append(
                {
                    "id": approval_request.id,
                    "form_code": approval_request.form_code,
                    "department": approval_request.department,
                    "status": approval_request.status,
                    "submitted_at": approval_request.submitted_at,
                    "reviewed_at": approval_request.reviewed_at,
                    "approver_comment": (
                        approval_request.approver_comment
                    ),
                }
            )

        return Response(
            data,
            status=status.HTTP_200_OK,
        )


class ApprovalRequestListView(APIView):

    permission_classes = [
        IsAuthenticated,
        # IsApprovalAdministrator,
    ]

    def get(self, request):

        queryset = (
            ApprovalRequest.objects
            .select_related(
                "user",
                "reviewed_by",
            )
            .all()
            .order_by(
                "-submitted_at"
            )
        )

        request_status = request.query_params.get(
            "status"
        )

        department = request.query_params.get(
            "department"
        )

        form_code = request.query_params.get(
            "form_code"
        )

        search = request.query_params.get(
            "search"
        )

        if request_status:

            queryset = queryset.filter(
                status=request_status.upper()
            )

        if department:

            queryset = queryset.filter(
                department=department
            )

        if form_code:

            queryset = queryset.filter(
                form_code=form_code
            )

        if search:

            from django.db.models import Q

            queryset = queryset.filter(
                Q(
                    user__username__icontains=search
                )
                | Q(
                    user__email__icontains=search
                )
                | Q(
                    form_code__icontains=search
                )
                | Q(
                    department__icontains=search
                )
            )

        serializer = ApprovalRequestSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ApprovalRequestStatsView(APIView):

    permission_classes = [
        IsAuthenticated,
        # IsApprovalAdministrator,
    ]

    def get(self, request):

        total = ApprovalRequest.objects.count()

        pending = ApprovalRequest.objects.filter(
            status=ApprovalRequest.STATUS_PENDING
        ).count()

        approved = ApprovalRequest.objects.filter(
            status=ApprovalRequest.STATUS_APPROVED
        ).count()

        rejected = ApprovalRequest.objects.filter(
            status=ApprovalRequest.STATUS_REJECTED
        ).count()

        today = timezone.localdate()

        today_count = ApprovalRequest.objects.filter(
            submitted_at__date=today
        ).count()

        return Response(
            {
                "total": total,
                "pending": pending,
                "approved": approved,
                "rejected": rejected,
                "today": today_count,
            },
            status=status.HTTP_200_OK,
        )


class ApprovalRequestDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
        # IsApprovalAdministrator,
    ]

    def get(self, request, request_id):

        try:

            approval_request = (
                ApprovalRequest.objects
                .select_related(
                    "user",
                    "reviewed_by",
                )
                .get(
                    pk=request_id
                )
            )

        except ApprovalRequest.DoesNotExist:

            return Response(
                {
                    "detail": (
                        "Approval request not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ApprovalRequestSerializer(
            approval_request
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ApproveApprovalRequestView(APIView):

    permission_classes = [
        IsAuthenticated,
        # IsApprovalAdministrator,
    ]

    def post(self, request, pk):

        try:

            approval_request = (
                ApprovalRequest.objects.get(
                    pk=pk
                )
            )

        except ApprovalRequest.DoesNotExist:

            return Response(
                {
                    "detail": (
                        "Approval request not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if approval_request.status != (
            ApprovalRequest.STATUS_PENDING
        ):

            return Response(
                {
                    "detail": (
                        "This request has already "
                        "been processed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        approval_request.status = (
            ApprovalRequest.STATUS_APPROVED
        )

        approval_request.reviewed_by = request.user

        approval_request.reviewed_at = timezone.now()

        approval_request.approver_comment = (
            str(
                request.data.get(
                    "approver_comment",
                    "",
                )
            ).strip()
        )

        approval_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "approver_comment",
            ]
        )

        serializer = ApprovalRequestSerializer(
            approval_request
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class RejectApprovalRequestView(APIView):

    permission_classes = [
        IsAuthenticated,
        # IsApprovalAdministrator,
    ]

    def post(self, request, pk):

        try:

            approval_request = (
                ApprovalRequest.objects.get(
                    pk=pk
                )
            )

        except ApprovalRequest.DoesNotExist:

            return Response(
                {
                    "detail": (
                        "Approval request not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if approval_request.status != (
            ApprovalRequest.STATUS_PENDING
        ):

            return Response(
                {
                    "detail": (
                        "This request has already "
                        "been processed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        approval_request.status = (
            ApprovalRequest.STATUS_REJECTED
        )

        approval_request.reviewed_by = request.user

        approval_request.reviewed_at = timezone.now()

        approval_request.approver_comment = (
            str(
                request.data.get(
                    "approver_comment",
                    "",
                )
            ).strip()
        )

        approval_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "approver_comment",
            ]
        )

        serializer = ApprovalRequestSerializer(
            approval_request
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class EmailApprovalDecisionView(APIView):

    authentication_classes = []

    permission_classes = [IsAuthenticated]

    def get(
        self,
        request,
        token,
        decision,
    ):

        if decision not in [
            "approve",
            "reject",
        ]:

            return HttpResponse(
                """
                <h2>Invalid Approval Decision</h2>
                <p>The requested action is not valid.</p>
                """,
                status=400,
            )

        try:

            data = loads(
                token,
                salt="approval-decision",
                max_age=60 * 60 * 24,
            )

        except SignatureExpired:

            return HttpResponse(
                """
                <h2>Link Expired</h2>
                <p>
                    This approval link has expired.
                    Please submit the request again.
                </p>
                """,
                status=410,
            )

        except BadSignature:

            return HttpResponse(
                """
                <h2>Invalid Link</h2>
                <p>
                    This approval link is invalid.
                </p>
                """,
                status=400,
            )

        request_id = data.get(
            "request_id"
        )

        try:

            approval_request = (
                ApprovalRequest.objects.get(
                    pk=request_id
                )
            )

        except ApprovalRequest.DoesNotExist:

            return HttpResponse(
                """
                <h2>Request Not Found</h2>
                <p>
                    This approval request no longer exists.
                </p>
                """,
                status=404,
            )

        if approval_request.status != (
            ApprovalRequest.STATUS_PENDING
        ):

            return HttpResponse(
                f"""
                <!DOCTYPE html>

                <html>

                <head>
                    <title>
                        Request Already Processed
                    </title>
                </head>

                <body style="
                    font-family: Arial, sans-serif;
                    background: #f5f7fa;
                    padding: 50px;
                    text-align: center;
                ">

                <div style="
                    max-width: 500px;
                    margin: auto;
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                ">

                    <h1>
                        Request Already Processed
                    </h1>

                    <p>
                        This approval request has already
                        been processed.
                    </p>

                    <p>
                        Current status:
                        <strong>
                            {approval_request.status}
                        </strong>
                    </p>

                </div>

                </body>
                </html>
                """,
                status=200,
            )

        if decision == "approve":

            approval_request.status = (
                ApprovalRequest.STATUS_APPROVED
            )

            message = "Request Approved"

            detail = (
                "The request has been approved successfully."
            )

        else:

            approval_request.status = (
                ApprovalRequest.STATUS_REJECTED
            )

            message = "Request Rejected"

            detail = (
                "The request has been rejected."
            )

        approval_request.reviewed_at = timezone.now()

        approval_request.reviewed_by = None

        approval_request.save(
            update_fields=[
                "status",
                "reviewed_at",
                "reviewed_by",
            ]
        )

        employee_name = (
            approval_request.user.get_full_name()
        )

        if not employee_name:

            employee_name = (
                getattr(
                    approval_request.user,
                    "username",
                    "",
                )
                or approval_request.user.email
            )

        return HttpResponse(
            f"""
            <!DOCTYPE html>

            <html>

            <head>
                <title>{message}</title>
            </head>

            <body style="
                font-family: Arial, sans-serif;
                background: #f5f7fa;
                padding: 50px;
                text-align: center;
            ">

            <div style="
                max-width: 500px;
                margin: auto;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow:
                    0 2px 10px
                    rgba(0,0,0,0.08);
            ">

                <h1>{message}</h1>

                <p>{detail}</p>

                <p>
                    Form:
                    <strong>
                        {approval_request.form_code}
                    </strong>
                </p>

                <p>
                    Employee:
                    <strong>
                        {employee_name}
                    </strong>
                </p>

                <p>
                    Department:
                    <strong>
                        {approval_request.department}
                    </strong>
                </p>

            </div>

            </body>
            </html>
            """
        )
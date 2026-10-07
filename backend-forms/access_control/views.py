from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, loads
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone

import msal
import requests

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .department_routing import get_approval_department
from .email import send_approval_request_email
from .models import ApprovalRequest
from .serializers import ApprovalRequestSerializer


# ============================================================
# MICROSOFT ENTRA / GRAPH
# ============================================================

def get_employee_from_entra(email):
    """
    Find an employee directly in Microsoft Entra ID
    using Microsoft Graph application authentication.

    Required Microsoft Graph Application Permission:

        User.Read.All
    """

    email = str(email).strip().lower()

    if not email:
        return None

    # --------------------------------------------------------
    # CHECK REQUIRED SETTINGS
    # --------------------------------------------------------

    client_id = getattr(
        settings,
        "MICROSOFT_CLIENT_ID",
        None,
    )

    client_secret = getattr(
        settings,
        "MICROSOFT_CLIENT_SECRET",
        None,
    )

    authority = getattr(
        settings,
        "MICROSOFT_AUTHORITY",
        None,
    )

    if not client_id:
        raise RuntimeError(
            "MICROSOFT_CLIENT_ID is not configured."
        )

    if not client_secret:
        raise RuntimeError(
            "MICROSOFT_CLIENT_SECRET is not configured."
        )

    if not authority:
        raise RuntimeError(
            "MICROSOFT_AUTHORITY is not configured."
        )

    # --------------------------------------------------------
    # CREATE CONFIDENTIAL CLIENT
    # --------------------------------------------------------

    try:

        msal_app = msal.ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=authority,
        )

    except Exception as error:

        raise RuntimeError(
            "Microsoft Entra application could not be "
            f"initialized: {error}"
        )

    # --------------------------------------------------------
    # GET APPLICATION TOKEN
    # --------------------------------------------------------

    try:

        token_result = (
            msal_app.acquire_token_for_client(
                scopes=[
                    "https://graph.microsoft.com/.default"
                ]
            )
        )

    except Exception as error:

        raise RuntimeError(
            "Microsoft Entra token request failed: "
            f"{error}"
        )

    # --------------------------------------------------------
    # CHECK TOKEN RESULT
    # --------------------------------------------------------

    if "access_token" not in token_result:

        error_code = token_result.get(
            "error",
            "unknown_error",
        )

        error_description = token_result.get(
            "error_description",
            "No error description was returned.",
        )

        raise RuntimeError(
            "Microsoft Entra authorization failed. "
            f"Error: {error_code}. "
            f"Details: {error_description}"
        )

    access_token = token_result["access_token"]

    # --------------------------------------------------------
    # ESCAPE EMAIL FOR ODATA
    # --------------------------------------------------------

    safe_email = email.replace(
        "'",
        "''",
    )

    # --------------------------------------------------------
    # SEARCH MICROSOFT GRAPH
    # --------------------------------------------------------

    filter_query = (
        f"mail eq '{safe_email}' "
        f"or userPrincipalName eq '{safe_email}'"
    )

    try:

        response = requests.get(
            "https://graph.microsoft.com/v1.0/users",
            headers={
                "Authorization": (
                    f"Bearer {access_token}"
                )
            },
            params={
                "$filter": filter_query,
                "$select": (
                    "id,"
                    "displayName,"
                    "mail,"
                    "userPrincipalName,"
                    "department,"
                    "jobTitle,"
                    "givenName,"
                    "surname"
                ),
                "$top": "1",
            },
            timeout=15,
        )

    except requests.RequestException as error:

        raise RuntimeError(
            "Microsoft Graph could not be reached: "
            f"{error}"
        )

    # --------------------------------------------------------
    # GRAPH RESPONSE
    # --------------------------------------------------------

    if response.status_code != 200:

        try:
            graph_error = response.json()
        except ValueError:
            graph_error = response.text

        raise RuntimeError(
            "Microsoft Graph employee lookup failed. "
            f"HTTP {response.status_code}: "
            f"{graph_error}"
        )

    users = response.json().get(
        "value",
        [],
    )

    # --------------------------------------------------------
    # EMPLOYEE NOT FOUND
    # --------------------------------------------------------

    if not users:
        return None

    employee = users[0]

    employee_email = (
        employee.get("mail")
        or employee.get("userPrincipalName")
        or email
    )

    return {
        "entra_object_id": employee.get(
            "id",
            "",
        ),
        "name": employee.get(
            "displayName",
            "",
        ),
        "email": employee_email,
        "department": employee.get(
            "department",
            "",
        ),
        "job_title": employee.get(
            "jobTitle",
            "",
        ),
        "given_name": employee.get(
            "givenName",
            "",
        ),
        "surname": employee.get(
            "surname",
            "",
        ),
    }


# ============================================================
# SUBMIT APPROVAL REQUEST
# ============================================================

class SubmitApprovalRequestView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        form_code = request.data.get(
            "form_code"
        )

        if not form_code:

            return Response(
                {
                    "detail": (
                        "form_code is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        form_code = str(
            form_code
        ).strip()

        reason = str(
            request.data.get(
                "reason",
                "",
            )
        ).strip()

        submission_data = request.data.get(
            "submission_data",
            {},
        )

        if not isinstance(
            submission_data,
            dict,
        ):
            submission_data = {}

        # ====================================================
        # REQUESTED EMPLOYEE EMAIL
        # ====================================================

        requested_for_email = str(
            request.data.get(
                "requested_for_email",
                "",
            )
        ).strip().lower()

        # ----------------------------------------------------
        # FALLBACK: employee.email
        # ----------------------------------------------------

        if not requested_for_email:

            employee = request.data.get(
                "employee",
                {},
            )

            if isinstance(
                employee,
                dict,
            ):

                requested_for_email = str(
                    employee.get(
                        "email",
                        "",
                    )
                ).strip().lower()

        # ----------------------------------------------------
        # FALLBACK: SUBMISSION DATA
        # ----------------------------------------------------

        if not requested_for_email:

            requested_for_email = (
                self._find_email(
                    submission_data
                )
            )

        # ====================================================
        # VALIDATE EMAIL
        # ====================================================

        if not requested_for_email:

            return Response(
                {
                    "accessFor": (
                        "The email address of the employee "
                        "the access is being requested for "
                        "could not be determined."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not requested_for_email.endswith(
            "@optimum-g.com"
        ):

            return Response(
                {
                    "accessFor": (
                        "The requested employee must have "
                        "an @optimum-g.com email address."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ====================================================
        # FIND EMPLOYEE IN ENTRA
        # ====================================================

        try:

            requested_employee = (
                get_employee_from_entra(
                    requested_for_email
                )
            )

        except RuntimeError as error:

            return Response(
                {
                    "accessFor": str(error),
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        except Exception as error:

            return Response(
                {
                    "accessFor": (
                        "The requested employee could "
                        "not be verified in Microsoft Entra."
                    ),
                    "error": str(error),
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        # ====================================================
        # EMPLOYEE NOT FOUND
        # ====================================================

        if not requested_employee:

            return Response(
                {
                    "accessFor": (
                        "The employee could not be found "
                        "in Microsoft Entra."
                    ),
                    "email": requested_for_email,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ====================================================
        # REQUESTED EMPLOYEE DETAILS
        # ====================================================

        requested_for_name = str(
            requested_employee.get(
                "name",
                "",
            )
        ).strip()

        if not requested_for_name:

            requested_for_name = (
                requested_for_email
            )

        requested_for_email = str(
            requested_employee.get(
                "email",
                requested_for_email,
            )
        ).strip().lower()

        requested_for_department = str(
            requested_employee.get(
                "department",
                "",
            )
        ).strip()

        if not requested_for_department:

            return Response(
                {
                    "accessFor": (
                        "No department is configured "
                        "in Microsoft Entra for the "
                        "requested employee."
                    ),
                    "name": requested_for_name,
                    "email": requested_for_email,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ====================================================
        # APPROVAL ROUTING
        # ====================================================

        try:

            routing = get_approval_department(
                form_code,
                requested_for_department,
            )

        except ValueError as error:

            return Response(
                {
                    "detail": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not routing:

            return Response(
                {
                    "detail": (
                        "No approval department could "
                        "be determined."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not routing.get("department"):

            return Response(
                {
                    "detail": (
                        "Approval department was not "
                        "configured."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not routing.get("email"):

            return Response(
                {
                    "detail": (
                        "Approval department email was "
                        "not configured."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ====================================================
        # PREVENT DUPLICATE PENDING REQUEST
        # ====================================================

        existing = (
            ApprovalRequest.objects
            .filter(
                user=request.user,
                form_code=form_code,
                requested_for_email__iexact=(
                    requested_for_email
                ),
                status=(
                    ApprovalRequest.STATUS_PENDING
                ),
            )
            .first()
        )

        if existing:

            return Response(
                {
                    "detail": (
                        "A request for this employee "
                        "and form is already pending "
                        "approval."
                    ),
                    "id": existing.id,
                    "form_code": (
                        existing.form_code
                    ),
                    "requested_for_name": (
                        existing.requested_for_name
                    ),
                    "requested_for_email": (
                        existing.requested_for_email
                    ),
                    "requested_for_department": (
                        existing.requested_for_department
                    ),
                    "department": (
                        existing.department
                    ),
                    "status": (
                        existing.status
                    ),
                    "submitted_at": (
                        existing.submitted_at
                    ),
                },
                status=status.HTTP_200_OK,
            )

        # ====================================================
        # CREATE REQUEST
        # ====================================================

        approval_request = (
            ApprovalRequest.objects.create(
                user=request.user,

                requested_for_name=(
                    requested_for_name
                ),

                requested_for_email=(
                    requested_for_email
                ),

                requested_for_department=(
                    requested_for_department
                ),

                form_code=form_code,

                department=(
                    routing["department"]
                ),

                department_email=(
                    routing["email"]
                ),

                reason=reason,

                submission_data=(
                    submission_data
                ),

                status=(
                    ApprovalRequest.STATUS_PENDING
                ),
            )
        )

        # ====================================================
        # SEND APPROVAL EMAIL
        # ====================================================

        try:

            send_approval_request_email(
                approval_request
            )

        except Exception as error:

            approval_request.delete()

            return Response(
                {
                    "detail": (
                        "The request could not be "
                        "submitted because the approval "
                        "email could not be sent."
                    ),
                    "error": str(error),
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        return Response(
            {
                "id": approval_request.id,

                "form_code": (
                    approval_request.form_code
                ),

                "requested_for_name": (
                    approval_request.requested_for_name
                ),

                "requested_for_email": (
                    approval_request.requested_for_email
                ),

                "requested_for_department": (
                    approval_request.requested_for_department
                ),

                "department": (
                    approval_request.department
                ),

                "status": (
                    approval_request.status
                ),

                "submitted_at": (
                    approval_request.submitted_at
                ),
            },
            status=status.HTTP_201_CREATED,
        )

    def _find_email(self, data):

        if isinstance(data, dict):

            for key, value in data.items():

                key_lower = str(
                    key
                ).lower()

                if key_lower in [
                    "email",
                    "employeeemail",
                    "employee_email",
                    "requestedforemail",
                    "requested_for_email",
                    "requesteeemail",
                    "requestee_email",
                ]:

                    if isinstance(
                        value,
                        str,
                    ):

                        value = (
                            value
                            .strip()
                            .lower()
                        )

                        if (
                            "@" in value
                            and value.endswith(
                                "@optimum-g.com"
                            )
                        ):

                            return value

                result = self._find_email(
                    value
                )

                if result:
                    return result

        elif isinstance(data, list):

            for item in data:

                result = self._find_email(
                    item
                )

                if result:
                    return result

        return ""


# ============================================================
# MY APPROVAL REQUESTS
# ============================================================

class MyApprovalRequestsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        approval_requests = (
            ApprovalRequest.objects
            .filter(
                user=request.user
            )
            .order_by(
                "-submitted_at"
            )
        )

        data = []

        for approval_request in approval_requests:

            data.append(
                {
                    "id": approval_request.id,
                    "form_code": (
                        approval_request.form_code
                    ),
                    "requested_for_name": (
                        approval_request.requested_for_name
                    ),
                    "requested_for_email": (
                        approval_request.requested_for_email
                    ),
                    "requested_for_department": (
                        approval_request.requested_for_department
                    ),
                    "department": (
                        approval_request.department
                    ),
                    "status": (
                        approval_request.status
                    ),
                    "submitted_at": (
                        approval_request.submitted_at
                    ),
                    "reviewed_at": (
                        approval_request.reviewed_at
                    ),
                    "approver_comment": (
                        approval_request.approver_comment
                    ),
                }
            )

        return Response(
            data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# APPROVAL REQUEST LIST
# ============================================================

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

        request_status = (
            request.query_params.get(
                "status"
            )
        )

        department = (
            request.query_params.get(
                "department"
            )
        )

        form_code = (
            request.query_params.get(
                "form_code"
            )
        )

        search = (
            request.query_params.get(
                "search"
            )
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

            queryset = queryset.filter(
                Q(
                    user__username__icontains=search
                )
                | Q(
                    user__email__icontains=search
                )
                | Q(
                    requested_for_name__icontains=search
                )
                | Q(
                    requested_for_email__icontains=search
                )
                | Q(
                    requested_for_department__icontains=search
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


# ============================================================
# APPROVAL REQUEST STATISTICS
# ============================================================

class ApprovalRequestStatsView(APIView):

    permission_classes = [
        IsAuthenticated,
        # IsApprovalAdministrator,
    ]

    def get(self, request):

        total = (
            ApprovalRequest.objects.count()
        )

        pending = (
            ApprovalRequest.objects
            .filter(
                status=(
                    ApprovalRequest.STATUS_PENDING
                )
            )
            .count()
        )

        approved = (
            ApprovalRequest.objects
            .filter(
                status=(
                    ApprovalRequest.STATUS_APPROVED
                )
            )
            .count()
        )

        rejected = (
            ApprovalRequest.objects
            .filter(
                status=(
                    ApprovalRequest.STATUS_REJECTED
                )
            )
            .count()
        )

        today = timezone.localdate()

        today_count = (
            ApprovalRequest.objects
            .filter(
                submitted_at__date=today
            )
            .count()
        )

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


# ============================================================
# APPROVAL REQUEST DETAIL
# ============================================================

class ApprovalRequestDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
        # IsApprovalAdministrator,
    ]

    def get(
        self,
        request,
        request_id,
    ):

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


# ============================================================
# APPROVE APPROVAL REQUEST
# ============================================================

class ApproveApprovalRequestView(APIView):

    permission_classes = [
        IsAuthenticated,
        # IsApprovalAdministrator,
    ]

    def post(
        self,
        request,
        pk,
    ):

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

        approval_request.reviewed_by = (
            request.user
        )

        approval_request.reviewed_at = (
            timezone.now()
        )

        approval_request.approver_comment = str(
            request.data.get(
                "approver_comment",
                "",
            )
        ).strip()

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


# ============================================================
# REJECT APPROVAL REQUEST
# ============================================================

class RejectApprovalRequestView(APIView):

    permission_classes = [
        IsAuthenticated,
        # IsApprovalAdministrator,
    ]

    def post(
        self,
        request,
        pk,
    ):

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

        approval_request.reviewed_by = (
            request.user
        )

        approval_request.reviewed_at = (
            timezone.now()
        )

        approval_request.approver_comment = str(
            request.data.get(
                "approver_comment",
                "",
            )
        ).strip()

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


# ============================================================
# EMAIL APPROVAL DECISION
# ============================================================

class EmailApprovalDecisionView(APIView):

    authentication_classes = []

    permission_classes = [
        AllowAny
    ]

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
                <p>
                    The requested action is not valid.
                </p>
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

        if not request_id:

            return HttpResponse(
                """
                <h2>Invalid Approval Request</h2>
                <p>
                    The approval request ID is missing.
                </p>
                """,
                status=400,
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
                <h2>Request Already Processed</h2>

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

        approval_request.reviewed_at = (
            timezone.now()
        )

        approval_request.reviewed_by = None

        approval_request.save(
            update_fields=[
                "status",
                "reviewed_at",
                "reviewed_by",
            ]
        )

        employee_name = (
            approval_request.requested_for_name
            or approval_request.requested_for_email
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

                <h1>
                    {message}
                </h1>

                <p>
                    {detail}
                </p>

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
                    Email:
                    <strong>
                        {approval_request.requested_for_email}
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
            """,
            status=200,
        )
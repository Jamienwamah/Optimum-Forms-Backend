from .graph import get_graph_access_token
from html import escape

import msal
import requests

from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, loads
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .department_routing import get_approval_department
from .email import (
    get_access_product,
    get_requested_employee,
    send_approval_request_email,
    send_access_approval_email,
    send_access_decision_email,
)
from .models import ApprovalRequest
from .serializers import ApprovalRequestSerializer


# ============================================================
# CONFIGURATION
# ============================================================

COMPANY_EMAIL_DOMAIN = "@optimum-g.com"

INTERNAL_CONTROL_EMAIL = getattr(
    settings,
    "INTERNAL_CONTROL_EMAIL",
    getattr(
        settings,
        "IT_ACCESS_APPROVAL_EMAIL",
        "internalcontrol@optimum-g.com",
    ),
)

IT_SUBMITTER_GROUPS = getattr(
    settings,
    "IT_ACCESS_SUBMITTER_GROUPS",
    ["IT", "IT Support", "IT Team"],
)

APPROVAL_REVIEWER_GROUPS = getattr(
    settings,
    "APPROVAL_REVIEWER_GROUPS",
    [
        "Approval Administrators",
        "Internal Control",
        "IT",
        "IT Support",
        "IT Team",
    ],
)

INTERNAL_CONTROL_GROUPS = [
    "Internal Control",
    "Approval Administrators",
]

# Exact code configured in Django settings for WealthForge.
# Example setting:
# WEALTHFORGE_ACCESS_FORM_CODE = "YOUR_ACTUAL_ANGULAR_FORM_CODE"
WEALTHFORGE_ACCESS_FORM_CODE = str(
    getattr(settings, "WEALTHFORGE_ACCESS_FORM_CODE", "") or ""
).strip().upper()

# Explicitly authorized administrators may submit access requests
# on behalf of employees without being the assigned Entra manager.
ACCESS_REQUEST_ADMIN_EMAILS = {
    str(email).strip().lower()
    for email in getattr(
        settings,
        "ACCESS_REQUEST_ADMIN_EMAILS",
        ["ikechukwu.nwamah@optimum-g.com"],
    )
    if email
}

DEVICE_RELATED_FORMS = {
    "OGCM-REPLACEMENT",
    "OGCM-TROUBLESHOOTING",
    "OGCM-INFRASTRUCTURE",
    "OGFS-REPLACEMENT",
    "OGFS-TROUBLESHOOTING",
    "OGFS-INFRASTRUCTURE",
    "OST-ISSUE",
    "OST-TROUBLESHOOTING",
}

ACCESS_PRODUCT_FORMS = {
    "OST-ENCLUSIA-ACCESS",
}

if WEALTHFORGE_ACCESS_FORM_CODE:
    ACCESS_PRODUCT_FORMS.add(WEALTHFORGE_ACCESS_FORM_CODE)

ALLOWED_FORM_CODES = DEVICE_RELATED_FORMS | ACCESS_PRODUCT_FORMS


# ============================================================
# AUTHORIZATION HELPERS
# ============================================================

def user_has_any_group(user, group_names):
    if not user or not user.is_authenticated:
        return False

    if getattr(user, "is_superuser", False):
        return True

    return user.groups.filter(name__in=group_names).exists()


def is_authorized_it_submitter(user):
    return user_has_any_group(user, IT_SUBMITTER_GROUPS)


def is_authorized_reviewer(user):
    return user_has_any_group(user, APPROVAL_REVIEWER_GROUPS)


def is_internal_control_reviewer(user):
    return user_has_any_group(user, INTERNAL_CONTROL_GROUPS)


def is_access_request_administrator(user):
    if not user or not user.is_authenticated:
        return False

    if getattr(user, "is_superuser", False):
        return True

    email = str(getattr(user, "email", "") or "").strip().lower()

    if email in ACCESS_REQUEST_ADMIN_EMAILS:
        return True

    return user.groups.filter(
        name="Approval Administrators"
    ).exists()


def reviewer_permission_response():
    return Response(
        {
            "detail": (
                "You do not have permission to access "
                "or process approval requests."
            )
        },
        status=status.HTTP_403_FORBIDDEN,
    )


def is_company_email(email):
    email = str(email or "").strip().lower()
    return (
        email.endswith(COMPANY_EMAIL_DOMAIN)
        and email != COMPANY_EMAIL_DOMAIN
    )


def get_employee_email_from_payload(data):
    email_keys = {
        "email",
        "employeeemail",
        "employee_email",
        "requestedforemail",
        "requested_for_email",
        "requesteeemail",
        "requestee_email",
    }

    if isinstance(data, dict):
        for key, value in data.items():
            if (
                str(key).lower() in email_keys
                and isinstance(value, str)
            ):
                candidate = value.strip().lower()

                if is_company_email(candidate):
                    return candidate

            found = get_employee_email_from_payload(value)

            if found:
                return found

    elif isinstance(data, list):
        for item in data:
            found = get_employee_email_from_payload(item)

            if found:
                return found

    return ""


def html_page(title, message, status_code=200):
    return HttpResponse(
        f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
</head>
<body style="font-family:Arial,sans-serif;background:#f5f7fa;padding:30px">
<div style="max-width:600px;margin:30px auto;background:#fff;padding:30px;
border:1px solid #e1e6ee;border-radius:10px">
<h2>{escape(title)}</h2>
<p>{escape(message)}</p>
</div>
</body>
</html>""",
        status=status_code,
    )


# ============================================================
# MICROSOFT ENTRA / GRAPH
# ============================================================

def get_graph_access_token():
    client_id = getattr(settings, "MICROSOFT_CLIENT_ID", None)
    client_secret = getattr(settings, "MICROSOFT_CLIENT_SECRET", None)
    authority = getattr(settings, "MICROSOFT_AUTHORITY", None)

    if not client_id or not client_secret or not authority:
        raise RuntimeError(
            "Microsoft Entra application settings are incomplete."
        )

    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=authority,
    )

    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )

    access_token = result.get("access_token")

    if not access_token:
        raise RuntimeError(
            result.get(
                "error_description",
                "Unable to authenticate with Microsoft Graph.",
            )
        )

    return access_token


def get_employee_from_entra(email):
    email = str(email or "").strip().lower()

    if not is_company_email(email):
        return None

    token = get_graph_access_token()
    safe_email = email.replace("'", "''")

    response = requests.get(
        "https://graph.microsoft.com/v1.0/users",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "$filter": (
                f"mail eq '{safe_email}' "
                f"or userPrincipalName eq '{safe_email}'"
            ),
            "$select": (
                "id,displayName,mail,userPrincipalName,"
                "department,jobTitle"
            ),
            "$top": "1",
        },
        timeout=15,
    )

    if response.status_code != 200:
        raise RuntimeError(
            "Microsoft Graph employee lookup failed: "
            f"HTTP {response.status_code}"
        )

    users = response.json().get("value", [])

    if not users:
        return None

    employee = users[0]

    return {
        "entra_object_id": employee.get("id", ""),
        "name": employee.get("displayName", "") or "",
        "email": (
            employee.get("mail")
            or employee.get("userPrincipalName")
            or email
        ).strip().lower(),
        "department": employee.get("department", "") or "",
        "job_title": employee.get("jobTitle", "") or "",
        "access_token": token,
    }


def get_employee_manager(employee_id, access_token):
    if not employee_id or not access_token:
        raise RuntimeError(
            "Employee ID or Microsoft Graph access token is missing."
        )

    response = requests.get(
        f"https://graph.microsoft.com/v1.0/users/{employee_id}/manager",
        headers={"Authorization": f"Bearer {access_token}"},
        params={
            "$select": "id,displayName,mail,userPrincipalName",
        },
        timeout=15,
    )

    if response.status_code == 404:
        return None

    if response.status_code != 200:
        raise RuntimeError(
            "Microsoft Graph manager lookup failed: "
            f"HTTP {response.status_code}"
        )

    manager = response.json()

    return {
        "id": manager.get("id", ""),
        "name": manager.get("displayName", "") or "",
        "email": (
            manager.get("mail")
            or manager.get("userPrincipalName")
            or ""
        ).strip().lower(),
    }


def get_verified_submitter_entra_id(user):
    """
    Read the Entra object ID linked to the authenticated Django user.
    The EntraProfile must be correctly linked to this user by your
    authentication/profile synchronization process.
    """
    profile = getattr(user, "entra_profile", None)

    return str(
        getattr(profile, "entra_object_id", "") or ""
    ).strip().lower()


# ============================================================
# EMAIL NOTIFICATION
# ============================================================

def send_request_notification(approval_request):
    product, _, _ = get_access_product(
        approval_request.form_code
    )

    if product:
        send_access_approval_email(approval_request)
    else:
        send_approval_request_email(approval_request)


# ============================================================
# SUBMIT APPROVAL REQUEST
# ============================================================

class SubmitApprovalRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        form_code = str(
            request.data.get("form_code", "")
        ).strip().upper()

        if not form_code:
            return Response(
                {"detail": "form_code is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Never let unknown form codes fall through to another
        # authorization or routing branch.
        if form_code not in ALLOWED_FORM_CODES:
            return Response(
                {"detail": "Unsupported form code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = str(
            request.data.get("reason", "")
        ).strip()

        submission_data = request.data.get("submission_data", {})

        if not isinstance(submission_data, dict):
            return Response(
                {"detail": "submission_data must be a JSON object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product, _, _ = get_access_product(form_code)
        is_access_request = form_code in ACCESS_PRODUCT_FORMS

        if is_access_request and not product:
            return Response(
                {
                    "detail": (
                        "The access product is not configured "
                        "correctly for this form code."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Device and IT support requests are restricted to IT groups.
        if not is_access_request and not is_authorized_it_submitter(
            request.user
        ):
            return Response(
                {
                    "detail": (
                        "Only authorized IT personnel can submit "
                        "device and IT support requests."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        requested_for_email = str(
            request.data.get("requested_for_email", "")
        ).strip().lower()

        employee_payload = request.data.get("employee", {})

        if (
            not requested_for_email
            and isinstance(employee_payload, dict)
        ):
            requested_for_email = str(
                employee_payload.get("email", "")
            ).strip().lower()

        if not requested_for_email:
            requested_for_email = get_employee_email_from_payload(
                submission_data
            )

        if not is_company_email(requested_for_email):
            return Response(
                {
                    "detail": (
                        "Provide a valid @optimum-g.com email address "
                        "for the employee who needs access or support."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify the requested employee in Entra.
        try:
            requested_employee = get_employee_from_entra(
                requested_for_email
            )
        except Exception:
            return Response(
                {
                    "detail": (
                        "Unable to verify the employee in Microsoft "
                        "Entra. Please try again or contact IT Support."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if not requested_employee:
            return Response(
                {
                    "detail": (
                        "The employee could not be found "
                        "in Microsoft Entra."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        employee_info = {
            "name": requested_employee["name"],
            "email": requested_employee["email"],
            "department": requested_employee["department"],
        }

        # ----------------------------------------------------
        # ENCLUSIA / WEALTHFORGE
        # Only the assigned manager or an authorized administrator
        # can submit these requests.
        # ----------------------------------------------------
        if is_access_request:
            is_admin = is_access_request_administrator(request.user)

            if not is_admin:
                submitter_object_id = get_verified_submitter_entra_id(
                    request.user
                )

                if not submitter_object_id:
                    return Response(
                        {
                            "detail": (
                                "Your Microsoft Entra profile could not "
                                "be verified. Sign in again or contact "
                                "IT Support."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

                try:
                    manager = get_employee_manager(
                        requested_employee["entra_object_id"],
                        requested_employee["access_token"],
                    )
                except Exception:
                    return Response(
                        {
                            "detail": (
                                "Unable to verify the employee's assigned "
                                "manager in Microsoft Entra."
                            )
                        },
                        status=status.HTTP_503_SERVICE_UNAVAILABLE,
                    )

                if not manager:
                    return Response(
                        {
                            "detail": (
                                "The employee has no manager assigned "
                                "in Microsoft Entra. The request cannot "
                                "be submitted."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

                manager_id = str(
                    manager.get("id", "")
                ).strip().lower()

                if manager_id != submitter_object_id:
                    return Response(
                        {
                            "detail": (
                                "Only the employee's assigned manager "
                                "or an authorized administrator can "
                                "submit this access request."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            routing = {
                "department": "Internal Control",
                "email": INTERNAL_CONTROL_EMAIL,
            }

        # ----------------------------------------------------
        # DEVICE / IT SUPPORT REQUESTS
        # ----------------------------------------------------
        else:
            if not employee_info["department"]:
                return Response(
                    {
                        "detail": (
                            "No department is configured for this "
                            "employee in Microsoft Entra."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                routing = get_approval_department(
                    form_code,
                    employee_info["department"],
                )
            except ValueError as error:
                return Response(
                    {"detail": str(error)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if (
                not routing
                or not routing.get("department")
                or not routing.get("email")
            ):
                return Response(
                    {
                        "detail": (
                            "Approval routing is not configured "
                            "correctly for this form."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        submission_data = dict(submission_data)
        submission_data["_requested_for"] = employee_info

        # Prevent duplicate pending requests from the same submitter
        # for the same form and employee.
        pending_requests = ApprovalRequest.objects.filter(
            user=request.user,
            form_code=form_code,
            status=ApprovalRequest.STATUS_PENDING,
        )

        for existing in pending_requests:
            existing_employee = get_requested_employee(existing)

            if (
                existing_employee.get("email", "").strip().lower()
                == employee_info["email"].strip().lower()
            ):
                return Response(
                    {
                        "detail": (
                            "A request for this employee and form "
                            "is already pending approval."
                        ),
                        "id": existing.pk,
                        "status": existing.status,
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
            send_request_notification(approval_request)
        except Exception:
            return Response(
                {
                    "detail": (
                        "Your request was saved, but the approval "
                        "notification could not be sent. Contact IT "
                        "Support so the notification can be retried."
                    ),
                    "id": approval_request.pk,
                    "form_code": approval_request.form_code,
                    "status": approval_request.status,
                },
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(
            {
                "id": approval_request.pk,
                "form_code": approval_request.form_code,
                "department": approval_request.department,
                "status": approval_request.status,
                "submitted_at": approval_request.submitted_at,
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# MY APPROVAL REQUESTS
# ============================================================

class MyApprovalRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        requests_list = (
            ApprovalRequest.objects
            .filter(user=request.user)
            .order_by("-submitted_at")
        )

        data = []

        for item in requests_list:
            employee = get_requested_employee(item)

            data.append(
                {
                    "id": item.pk,
                    "form_code": item.form_code,
                    "requested_for_name": employee["name"],
                    "requested_for_email": employee["email"],
                    "requested_for_department": employee["department"],
                    "department": item.department,
                    "status": item.status,
                    "submitted_at": item.submitted_at,
                    "reviewed_at": item.reviewed_at,
                    "approver_comment": item.approver_comment,
                }
            )

        return Response(data, status=status.HTTP_200_OK)


# ============================================================
# APPROVAL REQUEST LIST
# ============================================================

class ApprovalRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_authorized_reviewer(request.user):
            return reviewer_permission_response()

        queryset = (
            ApprovalRequest.objects
            .select_related("user", "reviewed_by")
            .all()
            .order_by("-submitted_at")
        )

        request_status = request.query_params.get("status")
        department = request.query_params.get("department")
        form_code = request.query_params.get("form_code")
        search = request.query_params.get("search")

        if request_status:
            valid_statuses = {
                ApprovalRequest.STATUS_PENDING,
                ApprovalRequest.STATUS_APPROVED,
                ApprovalRequest.STATUS_REJECTED,
            }

            request_status = request_status.upper()

            if request_status not in valid_statuses:
                return Response(
                    {"detail": "Invalid status filter."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queryset = queryset.filter(status=request_status)

        if department:
            queryset = queryset.filter(department=department)

        if form_code:
            queryset = queryset.filter(form_code=form_code.strip().upper())

        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search)
                | Q(user__email__icontains=search)
                | Q(form_code__icontains=search)
                | Q(department__icontains=search)
                | Q(reason__icontains=search)
            )

        serializer = ApprovalRequestSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================
# APPROVAL REQUEST STATISTICS
# ============================================================

class ApprovalRequestStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_authorized_reviewer(request.user):
            return reviewer_permission_response()

        today = timezone.localdate()

        return Response(
            {
                "total": ApprovalRequest.objects.count(),
                "pending": ApprovalRequest.objects.filter(
                    status=ApprovalRequest.STATUS_PENDING
                ).count(),
                "approved": ApprovalRequest.objects.filter(
                    status=ApprovalRequest.STATUS_APPROVED
                ).count(),
                "rejected": ApprovalRequest.objects.filter(
                    status=ApprovalRequest.STATUS_REJECTED
                ).count(),
                "today": ApprovalRequest.objects.filter(
                    submitted_at__date=today
                ).count(),
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# APPROVAL REQUEST DETAIL
# ============================================================

class ApprovalRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, request_id):
        if not is_authorized_reviewer(request.user):
            return reviewer_permission_response()

        try:
            approval_request = (
                ApprovalRequest.objects
                .select_related("user", "reviewed_by")
                .get(pk=request_id)
            )
        except ApprovalRequest.DoesNotExist:
            return Response(
                {"detail": "Approval request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            ApprovalRequestSerializer(approval_request).data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# SHARED APPROVAL / REJECTION PROCESSING
# ============================================================

def process_approval_decision(request, pk, decision):
    if not is_authorized_reviewer(request.user):
        return reviewer_permission_response()

    if decision not in {"approve", "reject"}:
        return Response(
            {"detail": "Invalid approval decision."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        try:
            approval_request = (
                ApprovalRequest.objects
                .select_for_update()
                .get(pk=pk)
            )
        except ApprovalRequest.DoesNotExist:
            return Response(
                {"detail": "Approval request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_access_request = (
            approval_request.form_code in ACCESS_PRODUCT_FORMS
        )

        if (
            is_access_request
            and not is_internal_control_reviewer(request.user)
        ):
            return Response(
                {
                    "detail": (
                        "Only Internal Control or an approval "
                        "administrator can decide Enclusia and "
                        "WealthForge requests."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if approval_request.status != ApprovalRequest.STATUS_PENDING:
            return Response(
                {
                    "detail": (
                        "This request has already been processed."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        approval_request.status = (
            ApprovalRequest.STATUS_APPROVED
            if decision == "approve"
            else ApprovalRequest.STATUS_REJECTED
        )
        approval_request.reviewed_by = request.user
        approval_request.reviewed_at = timezone.now()
        approval_request.approver_comment = str(
            request.data.get("approver_comment", "")
        ).strip()

        approval_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "approver_comment",
            ]
        )

    # The decision is committed before attempting email delivery.
    if approval_request.form_code in ACCESS_PRODUCT_FORMS:
        try:
            send_access_decision_email(approval_request)
        except Exception:
            return Response(
                {
                    "detail": (
                        "The decision was recorded, but one or more "
                        "decision notifications failed. Contact IT "
                        "Support to retry the notifications."
                    ),
                    "id": approval_request.pk,
                    "status": approval_request.status,
                },
                status=status.HTTP_202_ACCEPTED,
            )

    return Response(
        ApprovalRequestSerializer(approval_request).data,
        status=status.HTTP_200_OK,
    )


# ============================================================
# APPROVE REQUEST
# ============================================================

class ApproveApprovalRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        return process_approval_decision(request, pk, "approve")


# ============================================================
# REJECT REQUEST
# ============================================================

class RejectApprovalRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        return process_approval_decision(request, pk, "reject")


# ============================================================
# EMAIL APPROVAL DECISION
# ============================================================

class EmailApprovalDecisionView(APIView):
    """
    Email links never change request status on GET.

    The reviewer must be authenticated and authorized to confirm
    a decision. This assumes the approval portal supports browser
    session authentication. If the project uses JWT-only
    authentication, implement the equivalent authenticated portal
    flow before enabling this endpoint.
    """

    permission_classes = [AllowAny]

    def get(self, request, token, decision):
        if decision not in {"approve", "reject"}:
            return html_page(
                "Invalid Approval Decision",
                "The requested decision is invalid.",
                400,
            )

        if not request.user.is_authenticated:
            return html_page(
                "Sign-in Required",
                "Sign in to the approval portal, then reopen this "
                "approval email link.",
                403,
            )

        if not is_authorized_reviewer(request.user):
            return html_page(
                "Access Denied",
                "Your account is not authorized to review requests.",
                403,
            )

        if (
            decision in {"approve", "reject"}
            and not is_internal_control_reviewer(request.user)
        ):
            # Email decision links are only for access products.
            # The request's form type is checked after loading it.
            pass

        try:
            data = loads(
                token,
                salt="approval-decision",
                max_age=60 * 60 * 24,
            )
        except SignatureExpired:
            return html_page(
                "Approval Link Expired",
                "Please contact Internal Control or IT Support.",
                410,
            )
        except BadSignature:
            return html_page(
                "Invalid Approval Link",
                "This approval link is invalid.",
                400,
            )

        try:
            approval_request = ApprovalRequest.objects.get(
                pk=data.get("request_id")
            )
        except (
            ApprovalRequest.DoesNotExist,
            TypeError,
            ValueError,
        ):
            return html_page(
                "Request Not Found",
                "The approval request could not be found.",
                404,
            )

        if approval_request.form_code not in ACCESS_PRODUCT_FORMS:
            return html_page(
                "Unsupported Request",
                "This email workflow only supports access-product "
                "requests. Use the approval portal for other requests.",
                403,
            )

        if not is_internal_control_reviewer(request.user):
            return html_page(
                "Access Denied",
                "Only Internal Control or an approval administrator "
                "can decide this access request.",
                403,
            )

        if approval_request.status != ApprovalRequest.STATUS_PENDING:
            return html_page(
                "Request Already Processed",
                f"Current status: {approval_request.status}",
                409,
            )

        product, _, _ = get_access_product(
            approval_request.form_code
        )
        safe_product = escape(product or "access")
        safe_decision = escape(decision.title())
        csrf_token = escape(get_token(request), quote=True)

        return HttpResponse(
            f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Confirm {safe_decision} - {safe_product}</title>
</head>
<body style="font-family:Arial,sans-serif;background:#f5f7fa;padding:30px">
<div style="max-width:560px;margin:30px auto;background:white;padding:30px;
border:1px solid #e1e6ee;border-radius:10px">
<h2>Confirm {safe_decision}</h2>
<p>You are about to <strong>{safe_decision.lower()}</strong> a
{safe_product} access request.</p>
<p>This will update the request and send decision notifications.</p>
<form method="post">
<input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
<input type="hidden" name="decision"
value="{escape(decision, quote=True)}">
<button type="submit" style="background:#12345a;color:white;border:0;
padding:12px 20px;border-radius:5px;cursor:pointer">
Confirm {safe_decision}
</button>
</form>
<p style="font-size:12px;color:#667085;margin-top:20px">
If you did not intend to review this request, close this page.
</p>
</div>
</body>
</html>""",
            status=200,
        )

    def post(self, request, token, decision):
        # The user must be signed in and authorized at decision time,
        # not just when the email was sent.
        if not request.user.is_authenticated:
            return html_page(
                "Sign-in Required",
                "Sign in to the approval portal and reopen the "
                "approval email link.",
                403,
            )

        if not is_authorized_reviewer(request.user):
            return html_page(
                "Access Denied",
                "Your account is not authorized to review requests.",
                403,
            )

        if decision not in {"approve", "reject"}:
            return html_page(
                "Invalid Approval Decision",
                "The requested decision is invalid.",
                400,
            )

        if request.data.get("decision") != decision:
            return html_page(
                "Invalid Confirmation",
                "Please reopen the approval email and try again.",
                400,
            )

        try:
            data = loads(
                token,
                salt="approval-decision",
                max_age=60 * 60 * 24,
            )
        except SignatureExpired:
            return html_page(
                "Approval Link Expired",
                "Please contact Internal Control or IT Support.",
                410,
            )
        except BadSignature:
            return html_page(
                "Invalid Approval Link",
                "This approval link is invalid.",
                400,
            )

        with transaction.atomic():
            try:
                approval_request = (
                    ApprovalRequest.objects
                    .select_for_update()
                    .get(pk=data.get("request_id"))
                )
            except (
                ApprovalRequest.DoesNotExist,
                TypeError,
                ValueError,
            ):
                return html_page(
                    "Request Not Found",
                    "The approval request could not be found.",
                    404,
                )

            if approval_request.form_code not in ACCESS_PRODUCT_FORMS:
                return html_page(
                    "Unsupported Request",
                    "This email workflow only supports access-product "
                    "requests.",
                    403,
                )

            if not is_internal_control_reviewer(request.user):
                return html_page(
                    "Access Denied",
                    "Only Internal Control or an approval "
                    "administrator can decide this request.",
                    403,
                )

            if approval_request.status != ApprovalRequest.STATUS_PENDING:
                return html_page(
                    "Request Already Processed",
                    f"Current status: {approval_request.status}",
                    409,
                )

            approval_request.status = (
                ApprovalRequest.STATUS_APPROVED
                if decision == "approve"
                else ApprovalRequest.STATUS_REJECTED
            )
            approval_request.reviewed_at = timezone.now()
            approval_request.reviewed_by = request.user

            # Email decisions may optionally include a comment.
            approval_request.approver_comment = str(
                request.data.get("approver_comment", "")
            ).strip()

            approval_request.save(
                update_fields=[
                    "status",
                    "reviewed_at",
                    "reviewed_by",
                    "approver_comment",
                ]
            )

        try:
            # This helper must notify both the requesting manager
            # and the configured IT owner.
            send_access_decision_email(approval_request)
        except Exception:
            return html_page(
                "Decision Recorded",
                "The decision was saved, but one or more notification "
                "emails failed. Contact IT Support to retry them.",
                202,
            )

        message = (
            "Request Approved"
            if decision == "approve"
            else "Request Rejected"
        )

        return html_page(
            message,
            "The decision was recorded and the notification helper "
            "completed without reporting an error.",
            200,
        )


# import html
# import logging
# import boto3

# from django.conf import settings
# from django.core.signing import dumps
# from django.urls import reverse
# from django.utils import timezone

# from .models import ApprovalRequest


# logger = logging.getLogger(__name__)


# # ==========================================================
# # AMAZON SES EMAIL SENDER
# # ==========================================================

# def send_aws_email(to_email, subject, html_content, text_content=""):
#     """Send an email through Amazon SES."""

#     if not settings.DEFAULT_FROM_EMAIL:
#         raise RuntimeError("DEFAULT_FROM_EMAIL is not configured.")

#     if not to_email:
#         raise ValueError("A recipient email address is required.")

#     ses = boto3.client(
#         "ses",
#         region_name=settings.AWS_SES_REGION_NAME,
#         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#     )

#     response = ses.send_email(
#         Source=settings.DEFAULT_FROM_EMAIL,
#         Destination={"ToAddresses": [to_email]},
#         Message={
#             "Subject": {
#                 "Data": subject,
#                 "Charset": "UTF-8",
#             },
#             "Body": {
#                 "Text": {
#                     "Data": text_content or
#                     "Please view this email in an HTML-compatible email client.",
#                     "Charset": "UTF-8",
#                 },
#                 "Html": {
#                     "Data": html_content,
#                     "Charset": "UTF-8",
#                 },
#             },
#         },
#     )

#     return response["MessageId"]


# # ==========================================================
# # REQUESTER DETAILS
# # ==========================================================

# def get_requester_details(approval_request):
#     """
#     Retrieve the account that actually submitted the access request.
#     """

#     user = getattr(approval_request, "user", None)

#     if not user:
#         return {
#             "name": "Not provided",
#             "email": "",
#         }

#     name = (
#         user.get_full_name()
#         or getattr(user, "username", "")
#         or getattr(user, "email", "")
#         or "Not provided"
#     )

#     email = (
#         getattr(user, "email", "") or ""
#     ).strip()

#     return {
#         "name": name,
#         "email": email,
#     }


# # ==========================================================
# # APPROVAL URL GENERATION
# # ==========================================================

# def get_approval_urls(approval_request):
#     """Generate signed approval and rejection URLs."""

#     token = dumps(
#         {"request_id": approval_request.id},
#         salt="approval-decision",
#     )

#     approve_path = reverse(
#         "approval-decision",
#         kwargs={
#             "decision": "approve",
#             "token": token,
#         },
#     )

#     reject_path = reverse(
#         "approval-decision",
#         kwargs={
#             "decision": "reject",
#             "token": token,
#         },
#     )

#     base_url = getattr(
#         settings,
#         "ACCESS_PORTAL_BASE_URL",
#         "http://localhost:8000",
#     ).rstrip("/")

#     return (
#         f"{base_url}{approve_path}",
#         f"{base_url}{reject_path}",
#     )


# # ==========================================================
# # ACCESS PRODUCT IDENTIFICATION
# # ==========================================================

# def get_access_product(form_code):
#     """Identify supported access request products."""

#     code = str(form_code or "").strip().upper()

#     if "ENCLUSIA" in code:
#         return (
#             "Enclusia",
#             "Request for Enclusia Access",
#             "Access to Enclusia",
#         )

#     if "WEALTHFORGE" in code:
#         return (
#             "WealthForge",
#             "Request for WealthForge Access",
#             "Access to WealthForge",
#         )

#     return None, None, None


# # ==========================================================
# # REQUESTED EMPLOYEE DETAILS
# # ==========================================================

# def get_requested_employee(approval_request):
#     """Retrieve the employee who is being requested for access."""

#     submission_data = approval_request.submission_data or {}

#     employee = (
#         submission_data.get("verifiedAccessFor")
#         or submission_data.get("accessFor")
#         or submission_data.get("_requested_for")
#         or {}
#     )

#     name = (
#         approval_request.requested_for_name
#         or employee.get("name")
#         or ""
#     )

#     email = (
#         approval_request.requested_for_email
#         or employee.get("email")
#         or ""
#     )

#     department = (
#         approval_request.requested_for_department
#         or employee.get("department")
#         or ""
#     )

#     if not email:
#         raise ValueError(
#             "The requested employee email is missing."
#         )

#     return {
#         "name": name,
#         "email": email,
#         "department": department,
#     }


# # ==========================================================
# # STANDARD APPROVAL REQUEST EMAIL
# # ==========================================================

# def send_approval_request_email(
#     approval_request: ApprovalRequest,
# ):
#     """Send an approval email for a standard request."""

#     product, _, _ = get_access_product(
#         approval_request.form_code
#     )

#     if product:
#         return send_access_approval_email(approval_request)

#     approve_url, reject_url = get_approval_urls(
#         approval_request
#     )

#     requester = get_requester_details(approval_request)

#     requester_name = requester["name"]
#     requester_email = requester["email"]

#     subject = (
#         f"Approval Required - {approval_request.form_code}"
#     )

#     safe_name = html.escape(requester_name)
#     safe_email = html.escape(requester_email)
#     safe_department = html.escape(
#         approval_request.department or ""
#     )
#     safe_form = html.escape(
#         approval_request.form_code or ""
#     )
#     safe_reason = html.escape(
#         approval_request.reason or "No reason provided."
#     )
#     safe_approve_url = html.escape(approve_url, quote=True)
#     safe_reject_url = html.escape(reject_url, quote=True)

#     html_content = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <meta charset="UTF-8">
#         <title>Approval Required</title>
#     </head>
#     <body style="font-family:Arial,sans-serif;background:#f5f7fa;padding:30px">
#         <div style="max-width:650px;margin:auto;background:#fff;padding:30px;border-radius:8px">

#             <h2>Approval Required</h2>

#             <p>
#                 A new form has been submitted and requires
#                 approval from your department.
#             </p>

#             <p>
#                 <strong>Requester:</strong> {safe_name}<br>
#                 <strong>Requester Email:</strong> {safe_email}<br>
#                 <strong>Department:</strong> {safe_department}<br>
#                 <strong>Form:</strong> {safe_form}<br>
#                 <strong>Reason:</strong> {safe_reason}
#             </p>

#             <table role="presentation" cellpadding="0" cellspacing="0"
#                    border="0" style="margin:25px 0">
#                 <tr>
#                     <td bgcolor="#198754" style="border-radius:5px">
#                         <a href="{safe_approve_url}" target="_blank"
#                            style="display:inline-block;padding:12px 22px;
#                            font-family:Arial,sans-serif;font-weight:bold;
#                            color:#ffffff;text-decoration:none">
#                             APPROVE
#                         </a>
#                     </td>
#                     <td width="15"></td>
#                     <td bgcolor="#dc3545" style="border-radius:5px">
#                         <a href="{safe_reject_url}" target="_blank"
#                            style="display:inline-block;padding:12px 22px;
#                            font-family:Arial,sans-serif;font-weight:bold;
#                            color:#ffffff;text-decoration:none">
#                             REJECT
#                         </a>
#                     </td>
#                 </tr>
#             </table>

#             <p style="font-size:13px;color:#666">
#                 These approval links are valid for 24 hours.
#             </p>

#             <p>
#                 Regards,<br>
#                 Ikechukwu Nwamah<br>
#                 IT Support Engineer
#             </p>

#         </div>
#     </body>
#     </html>
#     """

#     text_content = f"""
# Approval Required

# A new form has been submitted and requires approval.

# Requester: {requester_name}
# Requester Email: {requester_email}
# Department: {approval_request.department}
# Form: {approval_request.form_code}
# Access Required: {approval_request.access_required or "No reason provided."}

# Approve: {approve_url}
# Reject: {reject_url}

# These approval links are valid for 24 hours.

# Regards,
# Ikechukwu Nwamah
# IT Support Engineer
# """

#     return send_aws_email(
#         to_email=approval_request.department_email,
#         subject=subject,
#         html_content=html_content,
#         text_content=text_content,
#     )


# # ==========================================================
# # ENCLUSIA / WEALTHFORGE INTERNAL CONTROL APPROVAL EMAIL
# # ==========================================================

# def send_access_approval_email(approval_request: ApprovalRequest):
#     """
#     Send Enclusia or WealthForge access requests
#     to the Internal Control team.
#     """

#     product, subject, _ = get_access_product(
#         approval_request.form_code
#     )

#     if not product:
#         raise ValueError(
#             "Unsupported access request form."
#         )

#     # Employee receiving access.
#     employee = get_requested_employee(approval_request)

#     # Person who actually submitted the request.
#     requester = get_requester_details(approval_request)

#     requester_name = requester["name"]
#     requester_email = requester["email"]

#     approve_url, reject_url = get_approval_urls(
#         approval_request
#     )

#     submitted_at = timezone.localtime(
#         approval_request.submitted_at
#     ).strftime("%d %B %Y, %I:%M %p")

#     safe_product = html.escape(product)
#     safe_subject = html.escape(subject)

#     safe_employee_name = html.escape(
#         employee["name"] or "Not provided"
#     )
#     safe_employee_email = html.escape(employee["email"])
#     safe_employee_department = html.escape(
#         employee["department"] or "Not specified"
#     )

#     safe_requester_name = html.escape(requester_name)
#     safe_requester_email = html.escape(
#         requester_email or "Not provided"
#     )

#     safe_access_required = html.escape(
#         approval_request.access_required or "No reason provided."
#     )
#     safe_date = html.escape(submitted_at)

#     safe_approve_url = html.escape(approve_url, quote=True)
#     safe_reject_url = html.escape(reject_url, quote=True)

#     html_content = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <meta charset="UTF-8">
#         <title>{safe_product} Access Request</title>
#     </head>

#     <body style="font-family:Arial,sans-serif;background:#f5f7fa;
#                  padding:30px;color:#243044">

#         <div style="max-width:680px;margin:auto;background:#fff;
#                     border:1px solid #e1e6ee;border-radius:8px;
#                     overflow:hidden">

#             <div style="background:#12345a;color:#fff;padding:22px 28px">
#                 <h2 style="margin:0">{safe_subject}</h2>
#             </div>

#             <div style="padding:28px">

#                 <p>Dear Internal Control Team,</p>

#                 <p>
#                     An <strong>{safe_product}</strong> access request
#                     has been submitted for your review and approval.
#                 </p>

#                 <table style="width:100%;border-collapse:collapse">

#                     <tr>
#                         <td style="padding:10px;border-bottom:1px solid #eee">
#                             <strong>Employee</strong>
#                         </td>
#                         <td style="padding:10px;border-bottom:1px solid #eee">
#                             {safe_employee_name}
#                         </td>
#                     </tr>

#                     <tr>
#                         <td style="padding:10px;border-bottom:1px solid #eee">
#                             <strong>Employee Email</strong>
#                         </td>
#                         <td style="padding:10px;border-bottom:1px solid #eee">
#                             {safe_employee_email}
#                         </td>
#                     </tr>

#                     <tr>
#                         <td style="padding:10px;border-bottom:1px solid #eee">
#                             <strong>Department</strong>
#                         </td>
#                         <td style="padding:10px;border-bottom:1px solid #eee">
#                             {safe_employee_department}
#                         </td>
#                     </tr>

#                     <tr>
#                         <td style="padding:10px;border-bottom:1px solid #eee">
#                             <strong>Requested By</strong>
#                         </td>
#                         <td style="padding:10px;border-bottom:1px solid #eee">
#                             {html.escape(requester_name)}
#                         </td>
#                     </tr>

#                     <tr>
#                         <td style="padding:10px;border-bottom:1px solid #eee">
#                             <strong>Requester Email</strong>
#                         </td>
#                         <td style="padding:10px;border-bottom:1px solid #eee">
#                             {safe_requester_email}
#                         </td>
#                     </tr>

#                     <tr>
#                         <td style="padding:10px;border-bottom:1px solid #eee">
#                             <strong>Date Submitted</strong>
#                         </td>
#                         <td style="padding:10px;border-bottom:1px solid #eee">
#                             {safe_date}
#                         </td>
#                     </tr>

#                     <tr>
#                         <td style="padding:10px;vertical-align:top">
#                             <strong>Reason</strong>
#                         </td>
#                         <td style="padding:10px">
#                             {safe_reason}
#                         </td>
#                     </tr>

#                 </table>

#                 <p>
#                     Please review this request and select
#                     your decision below.
#                 </p>

#                 <table role="presentation" cellpadding="0" cellspacing="0"
#                        border="0"
#                        style="margin:28px 0;border-collapse:collapse">
#                     <tr>
#                         <td align="center" bgcolor="#18794e"
#                             style="border-radius:5px">
#                             <a href="{safe_approve_url}" target="_blank"
#                                style="display:inline-block;padding:14px 24px;
#                                font-family:Arial,sans-serif;font-size:14px;
#                                font-weight:bold;color:#ffffff;
#                                text-decoration:none;border-radius:5px">
#                                 APPROVE REQUEST
#                             </a>
#                         </td>

#                         <td width="15"></td>

#                         <td align="center" bgcolor="#b42318"
#                             style="border-radius:5px">
#                             <a href="{safe_reject_url}" target="_blank"
#                                style="display:inline-block;padding:14px 24px;
#                                font-family:Arial,sans-serif;font-size:14px;
#                                font-weight:bold;color:#ffffff;
#                                text-decoration:none;border-radius:5px">
#                                 REJECT REQUEST
#                             </a>
#                         </td>
#                     </tr>
#                 </table>

#                 <p style="font-size:12px;color:#667085">
#                     These approval links expire after 24 hours.
#                 </p>

#                 <p>
#                     Regards,<br>
#                     <strong>Ikechukwu Nwamah</strong><br>
#                     <strong>IT Support Engineer</strong>
#                 </p>

#             </div>
#         </div>

#     </body>
#     </html>
#     """

#     text_content = f"""
# {subject}

# Dear Internal Control Team,

# A {product} access request has been submitted for your review.

# Employee: {employee['name'] or 'Not provided'}
# Employee Email: {employee['email']}
# Department: {employee['department'] or 'Not specified'}

# Requested By: {requester_name}
# Requester Email: {requester_email or 'Not provided'}

# Date Submitted: {submitted_at}

# Access Required: {approval_request.reason or 'No reason provided.'}

# Approve: {approve_url}
# Reject: {reject_url}

# These approval links expire after 24 hours.

# Regards,
# Ikechukwu Nwamah
# IT Support Engineer
# """

#     internal_control_email = getattr(
#         settings,
#         "INTERNAL_CONTROL_EMAIL",
#         "internal-control@optimum-g.com",
#     ).strip()

#     return send_aws_email(
#         to_email=internal_control_email,
#         subject=subject,
#         html_content=html_content,
#         text_content=text_content,
#     )


# # ==========================================================
# # ACCESS REQUEST DECISION NOTIFICATIONS
# # ==========================================================

# def send_access_decision_email(
#     approval_request: ApprovalRequest,
# ):
#     """
#     Notify the requester, requested employee and IT
#     after Internal Control approves or rejects an access request.
#     """

#     product, _, _ = get_access_product(
#         approval_request.form_code
#     )

#     if not product:
#         return {
#             "success": False,
#             "message": "This is not a supported access request.",
#         }

#     if approval_request.status not in {
#         ApprovalRequest.STATUS_APPROVED,
#         ApprovalRequest.STATUS_REJECTED,
#     }:
#         raise ValueError(
#             "The request does not have a final decision."
#         )

#     approved = (
#         approval_request.status
#         == ApprovalRequest.STATUS_APPROVED
#     )

#     decision = "Approved" if approved else "Rejected"

#     employee = get_requested_employee(approval_request)
#     requester = get_requester_details(approval_request)

#     employee_name = employee["name"] or "Employee"
#     employee_email = employee["email"]
#     employee_department = employee["department"] or "Not specified"

#     requester_email = requester["email"]
#     requester_name = requester["name"]

#     it_email = (
#         getattr(settings, "IT_ACCESS_DECISION_EMAIL", "") or ""
#     ).strip()

#     if not requester_email:
#         raise ValueError(
#             "The requester email is missing."
#         )

#     if not employee_email:
#         raise ValueError(
#             "The requested employee email is missing."
#         )

#     if not it_email:
#         raise RuntimeError(
#             "IT_ACCESS_DECISION_EMAIL is not configured in settings.py."
#         )

#     reviewed_at = (
#         approval_request.reviewed_at
#         or timezone.now()
#     )

#     decision_date = timezone.localtime(
#         reviewed_at
#     ).strftime("%d %B %Y, %I:%M %p")

#     comment = (
#         approval_request.approver_comment
#         or "No comments provided."
#     )

#     safe_product = html.escape(product)
#     safe_employee = html.escape(employee_name)
#     safe_employee_email = html.escape(employee_email)
#     safe_department = html.escape(employee_department)
#     safe_comment = html.escape(comment)
#     safe_date = html.escape(decision_date)
#     safe_decision = html.escape(decision)

#     color = "#18794e" if approved else "#b42318"

#     email_results = {}

#     def send_notification(
#         key,
#         recipient,
#         subject,
#         heading,
#         message,
#     ):
#         """Send one notification without blocking the others."""

#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <meta charset="UTF-8">
#             <title>{html.escape(subject)}</title>
#         </head>

#         <body style="font-family:Arial,sans-serif;background:#f5f7fa;
#                      padding:30px;color:#243044">

#             <div style="max-width:650px;margin:auto;background:#fff;
#                         border:1px solid #e1e6ee;border-radius:8px;
#                         overflow:hidden">

#                 <div style="background:#12345a;color:#fff;padding:22px 28px">
#                     <h2 style="margin:0">{html.escape(heading)}</h2>
#                 </div>

#                 <div style="padding:28px">

#                     <p>{message}</p>

#                     <div style="background:{color};color:#fff;padding:14px;
#                                 text-align:center;border-radius:5px;
#                                 font-weight:bold;margin:20px 0">
#                         Request {safe_decision}
#                     </div>

#                     <p>
#                         <strong>Employee:</strong> {safe_employee}<br>
#                         <strong>Employee Email:</strong> {safe_employee_email}<br>
#                         <strong>Department:</strong> {safe_department}<br>
#                         <strong>Platform:</strong> {safe_product}<br>
#                         <strong>Decision Date:</strong> {safe_date}
#                     </p>

#                     <p>
#                         <strong>Internal Control Comments:</strong><br>
#                         {safe_comment}
#                     </p>

#                     <p>
#                         Regards,<br>
#                         <strong>Ikechukwu Nwamah</strong><br>
#                         <strong>IT Support Engineer</strong>
#                     </p>

#                 </div>
#             </div>

#         </body>
#         </html>
#         """

#         text_content = f"""
# {heading}

# {message}

# Request: {decision}

# Employee: {employee_name}
# Employee Email: {employee_email}
# Department: {employee_department}
# Platform: {product}
# Decision Date: {decision_date}

# Internal Control Comments:
# {comment}

# Regards,
# Ikechukwu Nwamah
# IT Support Engineer
# """

#         try:
#             message_id = send_aws_email(
#                 to_email=recipient,
#                 subject=subject,
#                 html_content=html_content,
#                 text_content=text_content,
#             )

#             email_results[key] = {
#                 "success": True,
#                 "message_id": message_id,
#             }

#         except Exception as error:
#             logger.exception(
#                 "Failed to send %s access decision email to %s",
#                 key,
#                 recipient,
#             )

#             email_results[key] = {
#                 "success": False,
#                 "error": str(error),
#             }

#     # ------------------------------------------------------
#     # 1. NOTIFY THE PERSON WHO SUBMITTED THE REQUEST
#     # ------------------------------------------------------

#     if approved:
#         requester_message = (
#             f"The access request you submitted for "
#             f"{employee_name} to the {product} platform has been approved."
#         )
#     else:
#         requester_message = (
#             f"The access request you submitted for "
#             f"{employee_name} to the {product} platform has been rejected."
#         )

#     send_notification(
#         key="requester",
#         recipient=requester_email,
#         subject=f"{product} Access Request - {decision}",
#         heading=f"{product} Access Request {decision}",
#         message=(
#             f"Dear {html.escape(requester_name)},<br><br>"
#             f"{html.escape(requester_message)}"
#         ),
#     )

#     # ------------------------------------------------------
#     # 2. NOTIFY THE EMPLOYEE RECEIVING ACCESS
#     # ------------------------------------------------------

#     if approved:
#         employee_message = (
#             f"You have been approved for access to the {product} platform. "
#             "Access will be granted shortly by the IT Department. "
#             "You will be notified when access has been provisioned."
#         )
#     else:
#         employee_message = (
#             f"Your request for access to the {product} platform has been "
#             "rejected by Internal Control. Please contact the person "
#             "who submitted the request or the appropriate department "
#             "if you require clarification."
#         )

#     send_notification(
#         key="employee",
#         recipient=employee_email,
#         subject=f"{product} Access Request - {decision}",
#         heading=f"Your {product} Access Request",
#         message=(
#             f"Dear {html.escape(employee_name)},<br><br>"
#             f"{html.escape(employee_message)}"
#         ),
#     )

#     # ------------------------------------------------------
#     # 3. NOTIFY THE IT DEPARTMENT
#     # ------------------------------------------------------

#     if approved:
#         it_message = (
#             f"The request to access the {product} platform has been "
#             f"approved for {employee_name}. Kindly proceed to grant "
#             "the employee the required access."
#         )
#     else:
#         it_message = (
#             f"The request to access the {product} platform has been "
#             f"rejected for {employee_name}. Kindly do not grant access "
#             "to the employee based on this request."
#         )

#     send_notification(
#         key="it",
#         recipient=it_email,
#         subject=f"IT Action Required - {product} Access {decision}",
#         heading=f"{product} Access Decision - IT Notification",
#         message=(
#             f"Dear IT Team,<br><br>"
#             f"{html.escape(it_message)}"
#         ),
#     )

#     return {
#         "success": all(
#             result["success"]
#             for result in email_results.values()
#         ),
#         "decision": decision,
#         "emails": email_results,
#     }


import html
import logging

import boto3

from django.conf import settings
from django.core.signing import dumps
from django.urls import reverse
from django.utils import timezone

from .models import ApprovalRequest


logger = logging.getLogger(__name__)


# ==========================================================
# AMAZON SES EMAIL SENDER
# ==========================================================

def send_aws_email(
    to_email,
    subject,
    html_content,
    text_content=""
):
    """Send an email through Amazon SES."""

    from_email = getattr(
        settings,
        "DEFAULT_FROM_EMAIL",
        ""
    )

    region_name = getattr(
        settings,
        "AWS_SES_REGION_NAME",
        ""
    )

    access_key = getattr(
        settings,
        "AWS_ACCESS_KEY_ID",
        ""
    )

    secret_key = getattr(
        settings,
        "AWS_SECRET_ACCESS_KEY",
        ""
    )

    to_email = str(to_email or "").strip()

    if not from_email:
        raise RuntimeError(
            "DEFAULT_FROM_EMAIL is not configured."
        )

    if not region_name:
        raise RuntimeError(
            "AWS_SES_REGION_NAME is not configured."
        )

    if not access_key or not secret_key:
        raise RuntimeError(
            "AWS SES credentials are not configured."
        )

    if not to_email:
        raise ValueError(
            "A recipient email address is required."
        )

    ses = boto3.client(
        "ses",
        region_name=region_name,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    response = ses.send_email(
        Source=from_email,
        Destination={
            "ToAddresses": [
                to_email
            ]
        },
        Message={
            "Subject": {
                "Data": subject,
                "Charset": "UTF-8",
            },
            "Body": {
                "Text": {
                    "Data": (
                        text_content
                        or
                        "Please view this email in an HTML-compatible email client."
                    ),
                    "Charset": "UTF-8",
                },
                "Html": {
                    "Data": html_content,
                    "Charset": "UTF-8",
                },
            },
        },
    )

    message_id = response.get("MessageId")

    if not message_id:
        raise RuntimeError(
            "Amazon SES did not return an email message ID."
        )

    logger.info(
        "Amazon SES email accepted. Message ID: %s",
        message_id
    )

    return message_id


# ==========================================================
# REQUESTER DETAILS
# ==========================================================

def get_requester_details(approval_request):
    """
    Retrieve the account that actually submitted the request.
    """

    user = getattr(
        approval_request,
        "user",
        None
    )

    if not user:
        return {
            "name": "Not provided",
            "email": "",
        }

    name = (
        user.get_full_name()
        or getattr(user, "username", "")
        or getattr(user, "email", "")
        or "Not provided"
    )

    email = (
        getattr(user, "email", "") or ""
    ).strip()

    return {
        "name": name,
        "email": email,
    }


# ==========================================================
# APPROVAL URL GENERATION
# ==========================================================

def get_approval_urls(approval_request):
    """Generate signed approval and rejection URLs."""

    token = dumps(
        {
            "request_id": approval_request.id
        },
        salt="approval-decision",
    )

    approve_path = reverse(
        "approval-decision",
        kwargs={
            "decision": "approve",
            "token": token,
        },
    )

    reject_path = reverse(
        "approval-decision",
        kwargs={
            "decision": "reject",
            "token": token,
        },
    )

    base_url = getattr(
        settings,
        "ACCESS_PORTAL_BASE_URL",
        "http://localhost:8000",
    )

    base_url = str(base_url).rstrip("/")

    return (
        f"{base_url}{approve_path}",
        f"{base_url}{reject_path}",
    )


# ==========================================================
# ACCESS PRODUCT IDENTIFICATION
# ==========================================================

def get_access_product(form_code):
    """Identify supported access request products."""

    code = str(
        form_code or ""
    ).strip().upper()

    if "ENCLUSIA" in code:

        return (
            "Enclusia",
            "Request for Enclusia Access",
            "Access to Enclusia",
        )

    if "WEALTHFORGE" in code:

        return (
            "WealthForge",
            "Request for WealthForge Access",
            "Access to WealthForge",
        )

    return None, None, None


# ==========================================================
# REQUESTED EMPLOYEE DETAILS
# ==========================================================

def get_requested_employee(approval_request):
    """
    Retrieve the employee who is receiving access.

    Supports both the current Enclusia submission structure
    and the previous access-request submission structure.
    """

    submission_data = (
        getattr(
            approval_request,
            "submission_data",
            None
        )
        or {}
    )

    if not isinstance(submission_data, dict):
        submission_data = {}

    employee = (
        submission_data.get("verifiedAccessFor")
        or submission_data.get("accessFor")
        or submission_data.get("_requested_for")
        or {}
    )

    if not isinstance(employee, dict):
        employee = {}

    name = (
        getattr(
            approval_request,
            "requested_for_name",
            ""
        )
        or employee.get("name")
        or ""
    )

    email = (
        getattr(
            approval_request,
            "requested_for_email",
            ""
        )
        or employee.get("email")
        or ""
    )

    department = (
        getattr(
            approval_request,
            "requested_for_department",
            ""
        )
        or employee.get("department")
        or ""
    )

    email = str(email).strip()

    if not email:
        raise ValueError(
            "The requested employee email is missing."
        )

    return {
        "name": str(name),
        "email": email,
        "department": str(department),
    }


# ==========================================================
# STANDARD APPROVAL REQUEST EMAIL
# ==========================================================

def send_approval_request_email(
    approval_request: ApprovalRequest,
):
    """Send an approval email for a standard request."""

    product, _, _ = get_access_product(
        approval_request.form_code
    )

    # Enclusia and WealthForge use Internal Control routing.
    if product:

        return send_access_approval_email(
            approval_request
        )

    # ------------------------------------------------------
    # APPROVAL LINKS
    # ------------------------------------------------------

    approve_url, reject_url = get_approval_urls(
        approval_request
    )

    # ------------------------------------------------------
    # REQUESTER DETAILS
    # ------------------------------------------------------

    requester = get_requester_details(
        approval_request
    )

    requester_name = requester["name"]
    requester_email = requester["email"]

    # ------------------------------------------------------
    # EMAIL SUBJECT
    # ------------------------------------------------------

    subject = (
        f"Approval Required - "
        f"{approval_request.form_code}"
    )

    # ------------------------------------------------------
    # EMAIL CONTENT
    # ------------------------------------------------------

    reason = (
        getattr(
            approval_request,
            "reason",
            ""
        )
        or "No reason provided."
    )

    safe_name = html.escape(
        str(requester_name)
    )

    safe_email = html.escape(
        str(requester_email)
    )

    safe_department = html.escape(
        str(
            approval_request.department or ""
        )
    )

    safe_form = html.escape(
        str(
            approval_request.form_code or ""
        )
    )

    safe_reason = html.escape(
        str(reason)
    )

    safe_approve_url = html.escape(
        approve_url,
        quote=True
    )

    safe_reject_url = html.escape(
        reject_url,
        quote=True
    )

    # ------------------------------------------------------
    # HTML EMAIL
    # ------------------------------------------------------

    html_content = f"""
    <!DOCTYPE html>
    <html>

    <head>
        <meta charset="UTF-8">
        <title>Approval Required</title>
    </head>

    <body style="font-family:Arial,sans-serif;
                 background:#f5f7fa;
                 padding:30px">

        <div style="max-width:650px;
                    margin:auto;
                    background:#fff;
                    padding:30px;
                    border-radius:8px">

            <h2>Approval Required</h2>

            <p>
                A new form has been submitted and requires
                approval from your department.
            </p>

            <p>
                <strong>Requester:</strong> {safe_name}<br>

                <strong>Requester Email:</strong> {safe_email}<br>

                <strong>Department:</strong> {safe_department}<br>

                <strong>Form:</strong> {safe_form}<br>

                <strong>Reason:</strong> {safe_reason}
            </p>

            <table role="presentation"
                   cellpadding="0"
                   cellspacing="0"
                   border="0"
                   style="margin:25px 0">

                <tr>

                    <td bgcolor="#198754"
                        style="border-radius:5px">

                        <a href="{safe_approve_url}"
                           target="_blank"
                           style="display:inline-block;
                                  padding:12px 22px;
                                  font-family:Arial,sans-serif;
                                  font-weight:bold;
                                  color:#ffffff;
                                  text-decoration:none">

                            APPROVE

                        </a>

                    </td>

                    <td width="15"></td>

                    <td bgcolor="#dc3545"
                        style="border-radius:5px">

                        <a href="{safe_reject_url}"
                           target="_blank"
                           style="display:inline-block;
                                  padding:12px 22px;
                                  font-family:Arial,sans-serif;
                                  font-weight:bold;
                                  color:#ffffff;
                                  text-decoration:none">

                            REJECT

                        </a>

                    </td>

                </tr>

            </table>

            <p style="font-size:13px;color:#666">
                These approval links are valid for 24 hours.
            </p>

            <p>
                Regards,<br>
                Ikechukwu Nwamah<br>
                IT Support Engineer
            </p>

        </div>

    </body>
    </html>
    """

    # ------------------------------------------------------
    # PLAIN TEXT EMAIL
    # ------------------------------------------------------

    text_content = f"""
Approval Required

A new form has been submitted and requires approval.

Requester: {requester_name}
Requester Email: {requester_email}
Department: {approval_request.department}
Form: {approval_request.form_code}
Reason: {reason}

Approve: {approve_url}
Reject: {reject_url}

These approval links are valid for 24 hours.

Regards,
Ikechukwu Nwamah
IT Support Engineer
"""

    # ------------------------------------------------------
    # SEND EMAIL
    # ------------------------------------------------------

    return send_aws_email(
        to_email=approval_request.department_email,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )


# ==========================================================
# ENCLUSIA / WEALTHFORGE INTERNAL CONTROL APPROVAL EMAIL
# ==========================================================

def send_access_approval_email(
    approval_request: ApprovalRequest
):
    """
    Send Enclusia or WealthForge access requests
    to the Internal Control team.
    """

    # ------------------------------------------------------
    # IDENTIFY PRODUCT
    # ------------------------------------------------------

    product, subject, _ = get_access_product(
        approval_request.form_code
    )

    if not product:

        raise ValueError(
            "Unsupported access request form."
        )

    # ------------------------------------------------------
    # RETRIEVE SUBMISSION DATA
    # ------------------------------------------------------

    submission_data = (
        getattr(
            approval_request,
            "submission_data",
            None
        )
        or {}
    )

    if not isinstance(submission_data, dict):

        raise ValueError(
            "The approval request submission data is invalid."
        )

    enclusia_data = (
        submission_data.get("enclusiaAccess")
        or {}
    )

    if not isinstance(enclusia_data, dict):
        enclusia_data = {}

    # ------------------------------------------------------
    # GET EMPLOYEE RECEIVING ACCESS
    # ------------------------------------------------------

    employee = get_requested_employee(
        approval_request
    )

    # ------------------------------------------------------
    # GET REQUESTER DETAILS
    # ------------------------------------------------------

    requester = get_requester_details(
        approval_request
    )

    requester_name = requester["name"]
    requester_email = requester["email"]

    # ------------------------------------------------------
    # GET REQUESTED ACCESS
    # ------------------------------------------------------

    access_required = (
        enclusia_data.get("accessRequired")
        or "Not specified"
    )

    # ------------------------------------------------------
    # GET JUSTIFICATION
    # ------------------------------------------------------

    justification = (
        getattr(
            approval_request,
            "reason",
            ""
        )
        or enclusia_data.get("justification")
        or "No reason provided."
    )

    # ------------------------------------------------------
    # GENERATE APPROVAL LINKS
    # ------------------------------------------------------

    approve_url, reject_url = get_approval_urls(
        approval_request
    )

    # ------------------------------------------------------
    # SUBMISSION DATE
    # ------------------------------------------------------

    submitted_at = (
        getattr(
            approval_request,
            "submitted_at",
            None
        )
        or timezone.now()
    )

    submitted_at = timezone.localtime(
        submitted_at
    ).strftime(
        "%d %B %Y, %I:%M %p"
    )

    # ------------------------------------------------------
    # ESCAPE HTML VALUES
    # ------------------------------------------------------

    safe_product = html.escape(
        str(product)
    )

    safe_subject = html.escape(
        str(subject)
    )

    safe_employee_name = html.escape(
        str(employee["name"] or "Not provided")
    )

    safe_employee_email = html.escape(
        str(employee["email"])
    )

    safe_employee_department = html.escape(
        str(employee["department"] or "Not specified")
    )

    safe_requester_name = html.escape(
        str(requester_name or "Not provided")
    )

    safe_requester_email = html.escape(
        str(requester_email or "Not provided")
    )

    safe_access_required = html.escape(
        str(access_required)
    )

    safe_reason = html.escape(
        str(justification)
    )

    safe_date = html.escape(
        str(submitted_at)
    )

    safe_approve_url = html.escape(
        approve_url,
        quote=True
    )

    safe_reject_url = html.escape(
        reject_url,
        quote=True
    )

    # ------------------------------------------------------
    # HTML EMAIL
    # ------------------------------------------------------

    html_content = f"""
    <!DOCTYPE html>
    <html>

    <head>
        <meta charset="UTF-8">
        <title>{safe_product} Access Request</title>
    </head>

    <body style="font-family:Arial,sans-serif;
                 background:#f5f7fa;
                 padding:30px;
                 color:#243044">

        <div style="max-width:680px;
                    margin:auto;
                    background:#fff;
                    border:1px solid #e1e6ee;
                    border-radius:8px;
                    overflow:hidden">

            <div style="background:#12345a;
                        color:#fff;
                        padding:22px 28px">

                <h2 style="margin:0">
                    {safe_subject}
                </h2>

            </div>

            <div style="padding:28px">

                <p>Dear Internal Control Team,</p>

                <p>
                    An <strong>{safe_product}</strong>
                    access request has been submitted
                    for your review and approval.
                </p>

                <table style="width:100%;
                              border-collapse:collapse">

                    <tr>
                        <td style="padding:10px;
                                   border-bottom:1px solid #eee">
                            <strong>Employee</strong>
                        </td>

                        <td style="padding:10px;
                                   border-bottom:1px solid #eee">
                            {safe_employee_name}
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:10px;
                                   border-bottom:1px solid #eee">
                            <strong>Employee Email</strong>
                        </td>

                        <td style="padding:10px;
                                   border-bottom:1px solid #eee">
                            {safe_employee_email}
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:10px;
                                   border-bottom:1px solid #eee">
                            <strong>Department</strong>
                        </td>

                        <td style="padding:10px;
                                   border-bottom:1px solid #eee">
                            {safe_employee_department}
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:10px;
                                   border-bottom:1px solid #eee">
                            <strong>Requested By</strong>
                        </td>

                        <td style="padding:10px;
                                   border-bottom:1px solid #eee">
                            {safe_requester_name}
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:10px;
                                   border-bottom:1px solid #eee">
                            <strong>Requester Email</strong>
                        </td>

                        <td style="padding:10px;
                                   border-bottom:1px solid #eee">
                            {safe_requester_email}
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:10px;
                                   border-bottom:1px solid #eee">
                            <strong>Access Required</strong>
                        </td>

                        <td style="padding:10px;
                                   border-bottom:1px solid #eee">
                            {safe_access_required}
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:10px;
                                   border-bottom:1px solid #eee;
                                   vertical-align:top">
                            <strong>Justification</strong>
                        </td>

                        <td style="padding:10px;
                                   border-bottom:1px solid #eee">
                            {safe_reason}
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:10px">
                            <strong>Date Submitted</strong>
                        </td>

                        <td style="padding:10px">
                            {safe_date}
                        </td>
                    </tr>

                </table>

                <p>
                    Please review this request and select
                    your decision below.
                </p>

                <table role="presentation"
                       cellpadding="0"
                       cellspacing="0"
                       border="0"
                       style="margin:28px 0;
                              border-collapse:collapse">

                    <tr>

                        <td align="center"
                            bgcolor="#18794e"
                            style="border-radius:5px">

                            <a href="{safe_approve_url}"
                               target="_blank"
                               style="display:inline-block;
                                      padding:14px 24px;
                                      font-family:Arial,sans-serif;
                                      font-size:14px;
                                      font-weight:bold;
                                      color:#ffffff;
                                      text-decoration:none;
                                      border-radius:5px">

                                APPROVE REQUEST

                            </a>

                        </td>

                        <td width="15"></td>

                        <td align="center"
                            bgcolor="#b42318"
                            style="border-radius:5px">

                            <a href="{safe_reject_url}"
                               target="_blank"
                               style="display:inline-block;
                                      padding:14px 24px;
                                      font-family:Arial,sans-serif;
                                      font-size:14px;
                                      font-weight:bold;
                                      color:#ffffff;
                                      text-decoration:none;
                                      border-radius:5px">

                                REJECT REQUEST

                            </a>

                        </td>

                    </tr>

                </table>

                <p style="font-size:12px;color:#667085">
                    These approval links expire after 24 hours.
                </p>

                <p>
                    Regards,<br>
                    <strong>Ikechukwu Nwamah</strong><br>
                    <strong>IT Support Engineer</strong>
                </p>

            </div>

        </div>

    </body>
    </html>
    """

    # ------------------------------------------------------
    # PLAIN TEXT EMAIL
    # ------------------------------------------------------

    text_content = f"""
{subject}

Dear Internal Control Team,

An {product} access request has been submitted for your review.

Employee: {employee['name'] or 'Not provided'}
Employee Email: {employee['email']}
Department: {employee['department'] or 'Not specified'}

Requested By: {requester_name}
Requester Email: {requester_email or 'Not provided'}

Access Required: {access_required}

Justification: {justification}

Date Submitted: {submitted_at}

Approve: {approve_url}
Reject: {reject_url}

These approval links expire after 24 hours.

Regards,
Ikechukwu Nwamah
IT Support Engineer
"""

    # ------------------------------------------------------
    # INTERNAL CONTROL RECIPIENT
    # ------------------------------------------------------

    internal_control_email = getattr(
        settings,
        "INTERNAL_CONTROL_EMAIL",
        "internal-control@optimum-g.com",
    )

    internal_control_email = str(
        internal_control_email or ""
    ).strip()

    if not internal_control_email:

        raise RuntimeError(
            "INTERNAL_CONTROL_EMAIL is not configured."
        )

    # ------------------------------------------------------
    # SEND EMAIL THROUGH AMAZON SES
    # ------------------------------------------------------

    message_id = send_aws_email(
        to_email=internal_control_email,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )

    logger.info(
        "%s approval email sent successfully. "
        "Approval Request ID: %s. SES Message ID: %s",
        product,
        approval_request.id,
        message_id
    )

    return message_id


# ==========================================================
# ACCESS REQUEST DECISION NOTIFICATIONS
# ==========================================================

def send_access_decision_email(
    approval_request: ApprovalRequest,
):
    """
    Notify the requester, requested employee and IT
    after Internal Control approves or rejects an access request.
    """

    # ------------------------------------------------------
    # IDENTIFY PRODUCT
    # ------------------------------------------------------

    product, _, _ = get_access_product(
        approval_request.form_code
    )

    if not product:

        return {
            "success": False,
            "message": (
                "This is not a supported access request."
            ),
        }

    # ------------------------------------------------------
    # VERIFY FINAL DECISION
    # ------------------------------------------------------

    if approval_request.status not in {
        ApprovalRequest.STATUS_APPROVED,
        ApprovalRequest.STATUS_REJECTED,
    }:

        raise ValueError(
            "The request does not have a final decision."
        )

    approved = (
        approval_request.status
        == ApprovalRequest.STATUS_APPROVED
    )

    decision = (
        "Approved" if approved else "Rejected"
    )

    # ------------------------------------------------------
    # GET EMPLOYEE AND REQUESTER
    # ------------------------------------------------------

    employee = get_requested_employee(
        approval_request
    )

    requester = get_requester_details(
        approval_request
    )

    employee_name = (
        employee["name"] or "Employee"
    )

    employee_email = employee["email"]

    employee_department = (
        employee["department"] or "Not specified"
    )

    requester_email = requester["email"]

    requester_name = requester["name"]

    # ------------------------------------------------------
    # GET IT NOTIFICATION RECIPIENT
    # ------------------------------------------------------

    it_email = (
        getattr(
            settings,
            "IT_ACCESS_DECISION_EMAIL",
            ""
        )
        or ""
    ).strip()

    if not requester_email:

        raise ValueError(
            "The requester email is missing."
        )

    if not employee_email:

        raise ValueError(
            "The requested employee email is missing."
        )

    if not it_email:

        raise RuntimeError(
            "IT_ACCESS_DECISION_EMAIL is not configured in settings.py."
        )

    # ------------------------------------------------------
    # DECISION DATE AND COMMENTS
    # ------------------------------------------------------

    reviewed_at = (
        getattr(
            approval_request,
            "reviewed_at",
            None
        )
        or timezone.now()
    )

    decision_date = timezone.localtime(
        reviewed_at
    ).strftime(
        "%d %B %Y, %I:%M %p"
    )

    comment = (
        getattr(
            approval_request,
            "approver_comment",
            ""
        )
        or "No comments provided."
    )

    # ------------------------------------------------------
    # ESCAPE HTML VALUES
    # ------------------------------------------------------

    safe_product = html.escape(
        str(product)
    )

    safe_employee = html.escape(
        str(employee_name)
    )

    safe_employee_email = html.escape(
        str(employee_email)
    )

    safe_department = html.escape(
        str(employee_department)
    )

    safe_comment = html.escape(
        str(comment)
    )

    safe_date = html.escape(
        str(decision_date)
    )

    safe_decision = html.escape(
        str(decision)
    )

    color = (
        "#18794e" if approved else "#b42318"
    )

    # ------------------------------------------------------
    # EMAIL RESULT TRACKING
    # ------------------------------------------------------

    email_results = {}

    def send_notification(
        key,
        recipient,
        subject,
        heading,
        message,
    ):
        """Send an individual decision notification."""

        safe_subject = html.escape(
            str(subject)
        )

        safe_heading = html.escape(
            str(heading)
        )

        html_content = f"""
        <!DOCTYPE html>
        <html>

        <head>
            <meta charset="UTF-8">
            <title>{safe_subject}</title>
        </head>

        <body style="font-family:Arial,sans-serif;
                     background:#f5f7fa;
                     padding:30px;
                     color:#243044">

            <div style="max-width:650px;
                        margin:auto;
                        background:#fff;
                        border:1px solid #e1e6ee;
                        border-radius:8px;
                        overflow:hidden">

                <div style="background:#12345a;
                            color:#fff;
                            padding:22px 28px">

                    <h2 style="margin:0">
                        {safe_heading}
                    </h2>

                </div>

                <div style="padding:28px">

                    <p>{message}</p>

                    <div style="background:{color};
                                color:#fff;
                                padding:14px;
                                text-align:center;
                                border-radius:5px;
                                font-weight:bold;
                                margin:20px 0">

                        Request {safe_decision}

                    </div>

                    <p>
                        <strong>Employee:</strong> {safe_employee}<br>

                        <strong>Employee Email:</strong> {safe_employee_email}<br>

                        <strong>Department:</strong> {safe_department}<br>

                        <strong>Platform:</strong> {safe_product}<br>

                        <strong>Decision Date:</strong> {safe_date}
                    </p>

                    <p>
                        <strong>Internal Control Comments:</strong><br>
                        {safe_comment}
                    </p>

                    <p>
                        Regards,<br>
                        <strong>Ikechukwu Nwamah</strong><br>
                        <strong>IT Support Engineer</strong>
                    </p>

                </div>

            </div>

        </body>
        </html>
        """

        text_content = f"""
{heading}

{message}

Request: {decision}

Employee: {employee_name}
Employee Email: {employee_email}
Department: {employee_department}
Platform: {product}
Decision Date: {decision_date}

Internal Control Comments:
{comment}

Regards,
Ikechukwu Nwamah
IT Support Engineer
"""

        try:

            message_id = send_aws_email(
                to_email=recipient,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
            )

            email_results[key] = {
                "success": True,
                "message_id": message_id,
            }

        except Exception as error:

            logger.exception(
                "Failed to send %s access decision email to %s",
                key,
                recipient,
            )

            email_results[key] = {
                "success": False,
                "error": str(error),
            }

    # ------------------------------------------------------
    # 1. NOTIFY REQUESTER
    # ------------------------------------------------------

    if approved:

        requester_message = (
            f"The access request you submitted for "
            f"{employee_name} to the {product} platform "
            f"has been approved."
        )

    else:

        requester_message = (
            f"The access request you submitted for "
            f"{employee_name} to the {product} platform "
            f"has been rejected."
        )

    send_notification(
        key="requester",
        recipient=requester_email,
        subject=f"{product} Access Request - {decision}",
        heading=f"{product} Access Request {decision}",
        message=(
            f"Dear {html.escape(requester_name)},<br><br>"
            f"{html.escape(requester_message)}"
        ),
    )

    # ------------------------------------------------------
    # 2. NOTIFY EMPLOYEE RECEIVING ACCESS
    # ------------------------------------------------------

    if approved:

        employee_message = (
            f"You have been approved for access to the "
            f"{product} platform. Access will be granted "
            f"shortly by the IT Department. You will be "
            f"notified when access has been provisioned."
        )

    else:

        employee_message = (
            f"Your request for access to the {product} "
            f"platform has been rejected by Internal Control. "
            f"Please contact the person who submitted the "
            f"request or the appropriate department if you "
            f"require clarification."
        )

    send_notification(
        key="employee",
        recipient=employee_email,
        subject=f"{product} Access Request - {decision}",
        heading=f"Your {product} Access Request",
        message=(
            f"Dear {html.escape(employee_name)},<br><br>"
            f"{html.escape(employee_message)}"
        ),
    )

    # ------------------------------------------------------
    # 3. NOTIFY IT DEPARTMENT
    # ------------------------------------------------------

    if approved:

        it_message = (
            f"The request to access the {product} platform "
            f"has been approved for {employee_name}. "
            f"Kindly proceed to grant the employee the "
            f"required access."
        )

    else:

        it_message = (
            f"The request to access the {product} platform "
            f"has been rejected for {employee_name}. "
            f"Kindly do not grant access to the employee "
            f"based on this request."
        )

    send_notification(
        key="it",
        recipient=it_email,
        subject=(
            f"IT Action Required - {product} Access {decision}"
        ),
        heading=(
            f"{product} Access Decision - IT Notification"
        ),
        message=(
            f"Dear IT Team,<br><br>"
            f"{html.escape(it_message)}"
        ),
    )

    # ------------------------------------------------------
    # RETURN NOTIFICATION RESULTS
    # ------------------------------------------------------

    return {
        "success": all(
            result["success"]
            for result in email_results.values()
        ),
        "decision": decision,
        "emails": email_results,
    }


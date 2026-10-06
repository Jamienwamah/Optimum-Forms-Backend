import msal
import requests

from django.conf import settings
from django.core.signing import dumps
from django.urls import reverse

from .models import ApprovalRequest


def get_graph_access_token():

    authority = (
        f"https://login.microsoftonline.com/"
        f"{settings.MICROSOFT_TENANT_ID}"
    )

    app = msal.ConfidentialClientApplication(
        settings.MICROSOFT_CLIENT_ID,
        authority=authority,
        client_credential=settings.MICROSOFT_CLIENT_SECRET,
    )

    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )

    if "access_token" not in result:
        raise RuntimeError(
            f"Microsoft Graph authentication failed: "
            f"{result.get('error_description', result)}"
        )

    return result["access_token"]


def send_graph_email(
    to_email,
    subject,
    html_content,
    text_content="",
):

    token = get_graph_access_token()

    sender = settings.GRAPH_SENDER_EMAIL

    url = (
        f"https://graph.microsoft.com/v1.0/"
        f"users/{sender}/sendMail"
    )

    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": html_content,
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_email,
                    }
                }
            ],
        },
        "saveToSentItems": True,
    }

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    if response.status_code != 202:
        raise RuntimeError(
            f"Microsoft Graph email failed: "
            f"{response.status_code} {response.text}"
        )

    return True


def send_approval_request_email(
    approval_request: ApprovalRequest,
):

    token = dumps(
        {
            "request_id": approval_request.id,
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
    ).rstrip("/")

    approve_url = f"{base_url}{approve_path}"
    reject_url = f"{base_url}{reject_path}"

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

    subject = (
        f"Approval Required - "
        f"{approval_request.form_code}"
    )

    html_content = f"""
<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>Approval Required</title>
</head>

<body style="
    font-family: Arial, sans-serif;
    background-color: #f5f7fa;
    padding: 30px;
">

<div style="
    max-width: 650px;
    margin: auto;
    background: #ffffff;
    padding: 30px;
    border-radius: 8px;
">

    <h2>Approval Required</h2>

    <p>
        A new form has been submitted and requires
        approval from your department.
    </p>

    <table style="
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    ">

        <tr>
            <td style="padding: 8px 0;">
                <strong>Employee:</strong>
            </td>

            <td style="padding: 8px 0;">
                {employee_name}
            </td>
        </tr>

        <tr>
            <td style="padding: 8px 0;">
                <strong>Email:</strong>
            </td>

            <td style="padding: 8px 0;">
                {approval_request.user.email}
            </td>
        </tr>

        <tr>
            <td style="padding: 8px 0;">
                <strong>Department:</strong>
            </td>

            <td style="padding: 8px 0;">
                {approval_request.department}
            </td>
        </tr>

        <tr>
            <td style="padding: 8px 0;">
                <strong>Form:</strong>
            </td>

            <td style="padding: 8px 0;">
                {approval_request.form_code}
            </td>
        </tr>

        <tr>
            <td style="
                padding: 8px 0;
                vertical-align: top;
            ">
                <strong>Reason:</strong>
            </td>

            <td style="padding: 8px 0;">
                {approval_request.reason or "No reason provided."}
            </td>
        </tr>

    </table>

    <p>
        Please review the submitted request and select
        an action below.
    </p>

    <p>

        <a href="{approve_url}"
           style="
               display: inline-block;
               padding: 12px 22px;
               background-color: #198754;
               color: #ffffff;
               text-decoration: none;
               border-radius: 5px;
               margin-right: 10px;
           ">
            Approve
        </a>

        <a href="{reject_url}"
           style="
               display: inline-block;
               padding: 12px 22px;
               background-color: #dc3545;
               color: #ffffff;
               text-decoration: none;
               border-radius: 5px;
           ">
            Reject
        </a>

    </p>

    <p style="
        margin-top: 25px;
        font-size: 13px;
        color: #666666;
    ">
        These approval links are valid for 24 hours.
    </p>

    <p>
        Regards,<br>
        Optimum IT Support
    </p>

</div>

</body>
</html>
"""

    text_content = f"""
Approval Required

A new form has been submitted and requires approval.

Employee: {employee_name}
Email: {approval_request.user.email}
Department: {approval_request.department}
Form: {approval_request.form_code}

Reason:
{approval_request.reason or "No reason provided."}

Approve:
{approve_url}

Reject:
{reject_url}

These approval links are valid for 24 hours.

Regards,
Optimum IT Support
"""

    return send_graph_email(
        to_email=approval_request.department_email,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )
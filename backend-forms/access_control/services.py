from access_control.models import ApprovalRequest


def user_has_form_access(user, form_code):
    """
    Checks whether the user is authenticated.

    The current workflow does not require prior approval
    before a user can submit a form. Approval is created
    after the form is submitted and routed to the appropriate
    department.
    """

    if not user or not user.is_authenticated:
        return False

    return True


def create_approval_request(
    user,
    form_code,
    department,
    department_email,
    reason="",
    submission_data=None,
):
    """
    Creates an approval request after a form has been submitted.
    """

    if not user or not user.is_authenticated:
        raise ValueError("An authenticated user is required.")

    if not form_code:
        raise ValueError("Form code is required.")

    if not department:
        raise ValueError("Approval department is required.")

    if not department_email:
        raise ValueError("Approval department email is required.")

    if submission_data is None:
        submission_data = {}

    return ApprovalRequest.objects.create(
        user=user,
        form_code=form_code,
        department=department,
        department_email=department_email,
        reason=reason or "",
        submission_data=submission_data,
        status=ApprovalRequest.STATUS_PENDING,
    )


def approve_request(
    approval_request,
    reviewed_by=None,
    approver_comment="",
):
    """
    Approves a pending approval request.
    """

    if approval_request.status != ApprovalRequest.STATUS_PENDING:
        raise ValueError(
            "Only pending approval requests can be approved."
        )

    approval_request.status = ApprovalRequest.STATUS_APPROVED
    approval_request.reviewed_by = reviewed_by
    approval_request.approver_comment = approver_comment or ""

    from django.utils import timezone

    approval_request.reviewed_at = timezone.now()

    approval_request.save(
        update_fields=[
            "status",
            "reviewed_by",
            "approver_comment",
            "reviewed_at",
        ]
    )

    return approval_request


def reject_request(
    approval_request,
    reviewed_by=None,
    approver_comment="",
):
    """
    Rejects a pending approval request.
    """

    if approval_request.status != ApprovalRequest.STATUS_PENDING:
        raise ValueError(
            "Only pending approval requests can be rejected."
        )

    approval_request.status = ApprovalRequest.STATUS_REJECTED
    approval_request.reviewed_by = reviewed_by
    approval_request.approver_comment = approver_comment or ""

    from django.utils import timezone

    approval_request.reviewed_at = timezone.now()

    approval_request.save(
        update_fields=[
            "status",
            "reviewed_by",
            "approver_comment",
            "reviewed_at",
        ]
    )

    return approval_request

from rest_framework.permissions import BasePermission


APPROVAL_ADMIN_EMAILS = {
    "ikechukwu.nwamah@optimum-g.com",
}


class IsApprovalAdministrator(BasePermission):
    """
    Allows only explicitly authorised approval administrators
    and Django superusers to manage approval requests.
    """

    message = (
        "You do not have permission to manage form approval requests."
    )

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if getattr(user, "is_superuser", False):
            return True

        email = (
            getattr(user, "email", "") or ""
        ).strip().lower()

        authorised_emails = {
            address.strip().lower()
            for address in APPROVAL_ADMIN_EMAILS
        }

        return email in authorised_emails


from rest_framework.permissions import BasePermission


APPROVAL_REVIEWER_GROUPS = {
    "Approval Administrators",
    "Internal Control",
}

INTERNAL_CONTROL_GROUPS = {
    "Internal Control",
    "Approval Administrators",
}


def user_has_any_group(user, group_names):
    """
    Check whether an authenticated user belongs to at least
    one of the specified Django groups.
    """

    if not user or not user.is_authenticated:
        return False

    return user.groups.filter(name__in=group_names).exists()


def is_authorized_reviewer(user):
    """
    Only members of Approval Administrators or Internal Control
    can review approval requests.
    """

    return user_has_any_group(user, APPROVAL_REVIEWER_GROUPS)


def is_internal_control_reviewer(user):
    """
    Check whether the user belongs to an authorized
    Internal Control review group.
    """

    return user_has_any_group(user, INTERNAL_CONTROL_GROUPS)


class IsApprovalReviewer(BasePermission):
    message = (
        "You are not authorized to review approval requests."
    )

    def has_permission(self, request, view):
        return is_authorized_reviewer(request.user)


class IsInternalControlReviewer(BasePermission):
    message = (
        "You are not authorized to review Internal Control requests."
    )

    def has_permission(self, request, view):
        return is_internal_control_reviewer(request.user)

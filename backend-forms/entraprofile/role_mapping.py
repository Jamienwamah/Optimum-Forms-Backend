from django.conf import settings

from .models import EntraProfile


def resolve_dashboard_role(entra_roles):

    roles = {
        str(role).strip().lower()
        for role in (entra_roles or [])
    }

    super_admin_roles = {
        str(role).strip().lower()
        for role in getattr(
            settings,
            "MICROSOFT_DASHBOARD_SUPER_ADMIN_ROLES",
            [],
        )
    }

    admin_roles = {
        str(role).strip().lower()
        for role in getattr(
            settings,
            "MICROSOFT_DASHBOARD_ADMIN_ROLES",
            [],
        )
    }

    if roles.intersection(super_admin_roles):
        return EntraProfile.DASHBOARD_SUPER_ADMIN

    if roles.intersection(admin_roles):
        return EntraProfile.DASHBOARD_ADMIN

    return EntraProfile.DASHBOARD_APPROVER
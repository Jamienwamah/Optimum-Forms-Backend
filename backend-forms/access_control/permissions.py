# from rest_framework.permissions import BasePermission


# APPROVAL_ADMIN_EMAILS = {
#     "ikechukwu.nwamah@optimum-g.com",
# }


# class IsApprovalAdministrator(BasePermission):
#     """
#     Allows authorised users to manage form approval requests.
#     """

#     message = (
#         "You do not have permission to manage form approval requests."
#     )

#     def has_permission(self, request, view):

#         user = request.user

#         if not user or not user.is_authenticated:
#             return False

#         if user.is_superuser:
#             return True

#         email = (
#             getattr(user, "email", "")
#             or ""
#         ).strip().lower()

#         return email in {
#             address.lower()
#             for address in APPROVAL_ADMIN_EMAILS
#         }

from rest_framework.permissions import BasePermission


class IsApprovalAdministrator(BasePermission):

    message = (
        "You do not have permission to manage form approval requests."
    )

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        print("APPROVAL USER:", user)
        print("APPROVAL USERNAME:", getattr(user, "username", ""))
        print("APPROVAL EMAIL:", getattr(user, "email", ""))
        print("APPROVAL STAFF:", getattr(user, "is_staff", False))
        print("APPROVAL SUPERUSER:", getattr(user, "is_superuser", False))

        return True
# from django.conf import settings
# from django.contrib.auth import login, logout
# from django.contrib.auth.models import User
# from django.http import JsonResponse
# from django.shortcuts import redirect

# import msal

# from entraprofile.models import EntraProfile


# def get_msal_app():
#     """
#     Creates the Microsoft MSAL confidential client.
#     """

#     return msal.ConfidentialClientApplication(
#         client_id=settings.MICROSOFT_CLIENT_ID,
#         client_credential=settings.MICROSOFT_CLIENT_SECRET,
#         authority=settings.MICROSOFT_AUTHORITY,
#     )


# def microsoft_login(request):
#     """
#     Starts the Microsoft authentication flow.
#     """

#     msal_app = get_msal_app()

#     flow = msal_app.initiate_auth_code_flow(
#         scopes=settings.MICROSOFT_SCOPES,
#         redirect_uri=settings.MICROSOFT_REDIRECT_URI,
#     )

#     # Store the authentication flow in the Django session.
#     request.session["auth_flow"] = flow
#     request.session.save()

#     print("LOGIN SESSION KEY:", request.session.session_key)
#     print("LOGIN SESSION DATA:", dict(request.session))

#     return redirect(flow["auth_uri"])


# def microsoft_callback(request):
#     """
#     Handles Microsoft's response after authentication.
#     """

#     print("========== CALLBACK REACHED ==========")
#     print("SESSION KEY:", request.session.session_key)
#     print("SESSION DATA:", dict(request.session))

#     auth_flow = request.session.get("auth_flow")

#     if not auth_flow:
#         return JsonResponse(
#             {
#                 "status": "error",
#                 "message": "Authentication session expired or is invalid.",
#             },
#             status=400,
#         )

#     msal_app = get_msal_app()

#     try:
#         result = msal_app.acquire_token_by_auth_code_flow(
#             auth_flow,
#             request.GET,
#         )

#     except ValueError as e:
#         return JsonResponse(
#             {
#                 "status": "error",
#                 "message": str(e),
#             },
#             status=400,
#         )

#     # Remove the temporary authentication flow.
#     request.session.pop("auth_flow", None)

#     if "error" in result:
#         return JsonResponse(
#             {
#                 "status": "error",
#                 "message": result.get(
#                     "error_description",
#                     "Microsoft authentication failed.",
#                 ),
#             },
#             status=401,
#         )

#     user_claims = result.get(
#         "id_token_claims",
#         {}
#     )

#     email = user_claims.get(
#         "preferred_username"
#     )

#     name = user_claims.get(
#         "name",
#         ""
#     )

#     microsoft_user_id = user_claims.get(
#         "oid"
#     )

#     tenant_id = user_claims.get(
#         "tid"
#     )

#     # Make sure Microsoft actually returned the required identity.
#     if not email or not microsoft_user_id:
#         return JsonResponse(
#             {
#                 "status": "error",
#                 "message": "Microsoft account information could not be retrieved.",
#             },
#             status=400,
#         )

#     # Make sure the authentication came from our Microsoft tenant.
#     if tenant_id != settings.MICROSOFT_TENANT_ID:
#         return JsonResponse(
#             {
#                 "status": "error",
#                 "message": "Unauthorized Microsoft tenant.",
#             },
#             status=403,
#         )

#     # Restrict access to your company's email domain.
#     if not email.lower().endswith("@optimum-g.com"):
#         return JsonResponse(
#             {
#                 "status": "error",
#                 "message": "Access denied. Use your official company account.",
#             },
#             status=403,
#         )

#     # Create or retrieve the local Django user.
#     user, created = User.objects.get_or_create(
#         username=microsoft_user_id,
#         defaults={
#             "email": email,
#             "first_name": name,
#         },
#     )

#     # Keep the local user information updated.
#     user.email = email
#     user.first_name = name
#     user.save()

#     # Create or update the reusable Entra profile.
#     EntraProfile.objects.update_or_create(
#         user=user,
#         defaults={
#             "entra_object_id": microsoft_user_id,
#             "tenant_id": tenant_id,
#             "display_name": name,
#             "given_name": user_claims.get("given_name", ""),
#             "family_name": user_claims.get("family_name", ""),
#             "job_title": user_claims.get("job_title", ""),
#             "department": user_claims.get("department", ""),
#             "employee_id": user_claims.get("employee_id", ""),
#         },
#     )

#     # Create Django's authenticated session.
#     login(request, user)

#     return redirect("http://localhost:4200/")


# def current_user(request):
#     """
#     Returns the currently authenticated Django user.
#     """

#     if not request.user.is_authenticated:
#         return JsonResponse(
#             {
#                 "authenticated": False,
#             },
#             status=401,
#         )

#     return JsonResponse(
#         {
#             "authenticated": True,
#             "user": {
#                 "id": request.user.id,
#                 "email": request.user.email,
#                 "name": request.user.first_name,
#             },
#         }
#     )


# def logout_view(request):
#     """
#     Logs the user out of the Django application.
#     """

#     logout(request)

#     return JsonResponse(
#         {
#             "status": "success",
#             "message": "Successfully logged out.",
#         }
#     )

from entraprofile.role_mapping import resolve_dashboard_role
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect

import msal
import requests

from entraprofile.models import EntraProfile


def get_msal_app():
    """
    Creates the Microsoft MSAL confidential client.
    """

    return msal.ConfidentialClientApplication(
        client_id=settings.MICROSOFT_CLIENT_ID,
        client_credential=settings.MICROSOFT_CLIENT_SECRET,
        authority=settings.MICROSOFT_AUTHORITY,
    )


def microsoft_login(request):
    """
    Starts the Microsoft authentication flow.
    """

    msal_app = get_msal_app()

    flow = msal_app.initiate_auth_code_flow(
        scopes=settings.MICROSOFT_SCOPES,
        redirect_uri=settings.MICROSOFT_REDIRECT_URI,
    )

    # Store the authentication flow in the Django session.
    request.session["auth_flow"] = flow
    request.session.save()

    print(
        "LOGIN SESSION KEY:",
        request.session.session_key
    )

    print(
        "LOGIN SESSION DATA:",
        dict(request.session)
    )

    return redirect(flow["auth_uri"])


def microsoft_callback(request):
    """
    Handles Microsoft's response after authentication.
    """

    print(
        "========== CALLBACK REACHED =========="
    )

    print(
        "SESSION KEY:",
        request.session.session_key
    )

    print(
        "SESSION DATA:",
        dict(request.session)
    )

    auth_flow = request.session.get("auth_flow")

    if not auth_flow:
        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "Authentication session expired "
                    "or is invalid."
                ),
            },
            status=400,
        )

    msal_app = get_msal_app()

    try:

        result = msal_app.acquire_token_by_auth_code_flow(
            auth_flow,
            request.GET,
        )

    except ValueError as e:

        return JsonResponse(
            {
                "status": "error",
                "message": str(e),
            },
            status=400,
        )

    # Remove the temporary authentication flow.
    request.session.pop(
        "auth_flow",
        None
    )

    if "error" in result:

        return JsonResponse(
            {
                "status": "error",
                "message": result.get(
                    "error_description",
                    "Microsoft authentication failed.",
                ),
            },
            status=401,
        )

    # ---------------------------------------------------------
    # MICROSOFT ID TOKEN CLAIMS
    # ---------------------------------------------------------

    user_claims = result.get(
        "id_token_claims",
        {}
    )

    email = user_claims.get(
        "preferred_username",
        ""
    )

    name = user_claims.get(
        "name",
        ""
    )

    microsoft_user_id = user_claims.get(
        "oid"
    )

    tenant_id = user_claims.get(
        "tid"
    )

    # ---------------------------------------------------------
    # VALIDATE MICROSOFT IDENTITY
    # ---------------------------------------------------------

    if not email or not microsoft_user_id:

        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "Microsoft account information "
                    "could not be retrieved."
                ),
            },
            status=400,
        )

    # Make sure authentication came from our tenant.
    if tenant_id != settings.MICROSOFT_TENANT_ID:

        return JsonResponse(
            {
                "status": "error",
                "message": "Unauthorized Microsoft tenant.",
            },
            status=403,
        )

    # Restrict access to company accounts.
    if not email.lower().endswith(
        "@optimum-g.com"
    ):

        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "Access denied. Use your official "
                    "company account."
                ),
            },
            status=403,
        )

    # ---------------------------------------------------------
    # MICROSOFT GRAPH
    # ---------------------------------------------------------
    #
    # The ID token does not reliably contain:
    # - department
    # - jobTitle
    # - givenName
    # - surname
    #
    # These are retrieved from Microsoft Graph.
    # ---------------------------------------------------------

    access_token = result.get(
        "access_token"
    )
    entra_roles = get_entra_roles(
        access_token
        )
    dashboard_role = resolve_dashboard_role(
        entra_roles
)

    graph_data = {}

    if access_token:

        graph_response = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={
                "Authorization": (
                    f"Bearer {access_token}"
                )
            },
            params={
                "$select": (
                    "id,"
                    "displayName,"
                    "givenName,"
                    "surname,"
                    "jobTitle,"
                    "department"
                )
            },
            timeout=10,
        )

        if graph_response.status_code == 200:

            graph_data = graph_response.json()

            print(
                "MICROSOFT GRAPH USER DATA:",
                graph_data
            )

        else:

            print(
                "MICROSOFT GRAPH ERROR:",
                graph_response.status_code,
                graph_response.text
            )

    else:

        print(
            "MICROSOFT GRAPH ERROR: "
            "Access token was not returned."
        )

    # ---------------------------------------------------------
    # GET USER INFORMATION
    # ---------------------------------------------------------

    graph_object_id = graph_data.get(
        "id",
        microsoft_user_id
    )

    display_name = graph_data.get(
        "displayName"
    ) or name

    given_name = graph_data.get(
        "givenName",
        ""
    ) or ""

    family_name = graph_data.get(
        "surname",
        ""
    ) or ""

    department = graph_data.get(
        "department",
        ""
    ) or ""

    job_title = graph_data.get(
        "jobTitle",
        ""
    ) or ""

    # ---------------------------------------------------------
    # CREATE OR RETRIEVE LOCAL DJANGO USER
    # ---------------------------------------------------------

    user, created = User.objects.get_or_create(
        username=microsoft_user_id,
        defaults={
            "email": email,
            "first_name": display_name,
        },
    )

    # Keep local user information updated.
    user.email = email
    user.first_name = display_name
    user.save()

    # ---------------------------------------------------------
    # CREATE OR UPDATE ENTRA PROFILE
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    #
    # Employee ID is intentionally NOT overwritten here.
    #
    # It should be entered manually by the employee.
    # ---------------------------------------------------------

    profile, created = EntraProfile.objects.update_or_create(
        user=user,
        defaults={
            "entra_object_id": graph_object_id,
            "tenant_id": tenant_id,
            "display_name": display_name,
            "given_name": given_name,
            "family_name": family_name,
            "department": department,
            "job_title": job_title,
            "department": department,
            "entra_roles": entra_roles,
            "dashboard_role": dashboard_role,
        },
    )

    # ---------------------------------------------------------
    # DJANGO AUTHENTICATED SESSION
    # ---------------------------------------------------------

    login(
        request,
        user
    )

    return redirect(
        "http://localhost:4200/"
    )


def current_user(request):
    """
    Returns the currently authenticated Django user.
    """

    if not request.user.is_authenticated:

        return JsonResponse(
            {
                "authenticated": False,
            },
            status=401,
        )

    return JsonResponse(
        {
            "authenticated": True,
            "user": {
                "id": request.user.id,
                "email": request.user.email,
                "name": request.user.first_name,
            },
        }
    )
def get_entra_roles(access_token):

    if not access_token:
        return []

    response = requests.get(
        "https://graph.microsoft.com/v1.0/me/memberOf",
        headers={
            "Authorization": (
                f"Bearer {access_token}"
            )
        },
        params={
            "$select": (
                "id,"
                "displayName,"
                "roleTemplateId"
            )
        },
        timeout=10,
    )

    if response.status_code != 200:

        print(
            "MICROSOFT GRAPH ROLE ERROR:",
            response.status_code,
            response.text
        )

        return []

    roles = []

    for item in response.json().get(
        "value",
        []
    ):

        if item.get(
            "@odata.type"
        ) != "#microsoft.graph.directoryRole":

            continue

        display_name = item.get(
            "displayName"
        )

        if display_name:
            roles.append(
                display_name
            )

    return roles


def logout_view(request):
    """
    Logs the user out of the Django application.
    """

    logout(request)

    return JsonResponse(
        {
            "status": "success",
            "message": "Successfully logged out.",
        }
    )
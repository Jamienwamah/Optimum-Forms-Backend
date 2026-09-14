from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect

import msal


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

    print("LOGIN SESSION KEY:", request.session.session_key) 
    print("LOGIN SESSION DATA:", dict(request.session))

    return redirect(flow["auth_uri"])


def microsoft_callback(request):
    """
    Handles Microsoft's response after authentication.
    """
    print("========== CALLBACK REACHED ==========")
    print("SESSION KEY:", request.session.session_key) 
    print("SESSION DATA:", dict(request.session))

    auth_flow = request.session.get("auth_flow")

    if not auth_flow:
        return JsonResponse(
            {
                "status": "error",
                "message": "Authentication session expired or is invalid.",
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
    request.session.pop("auth_flow", None)

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

    user_claims = result.get(
        "id_token_claims",
        {}
    )

    email = user_claims.get(
        "preferred_username"
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

    # Make sure Microsoft actually returned the required identity.
    if not email or not microsoft_user_id:
        return JsonResponse(
            {
                "status": "error",
                "message": "Microsoft account information could not be retrieved.",
            },
            status=400,
        )

    # Make sure the authentication came from our Microsoft tenant.
    if tenant_id != settings.MICROSOFT_TENANT_ID:
        return JsonResponse(
            {
                "status": "error",
                "message": "Unauthorized Microsoft tenant.",
            },
            status=403,
        )

    # Restrict access to your company's email domain.
    if not email.lower().endswith("@optimum-g.com"):
        return JsonResponse(
            {
                "status": "error",
                "message": "Access denied. Use your official company account.",
            },
            status=403,
        )

    # Create or retrieve the local Django user.
    user, created = User.objects.get_or_create(
        username=microsoft_user_id,
        defaults={
            "email": email,
            "first_name": name,
        },
    )

    # Keep the local user information updated.
    user.email = email
    user.first_name = name

    user.save()

    # Create Django's authenticated session.
    login(request, user)

    return redirect("http://localhost:4200/")


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
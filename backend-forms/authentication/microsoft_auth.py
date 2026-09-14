import msal
from django.conf import settings


def get_msal_app():

    return msal.ConfidentialClientApplication(
        client_id=settings.MICROSOFT_CLIENT_ID,
        client_credential=settings.MICROSOFT_CLIENT_SECRET,
        authority=settings.MICROSOFT_AUTHORITY,
    )


def get_authorization_url():

    app = get_msal_app()

    return app.get_authorization_request_url(
        scopes=settings.MICROSOFT_SCOPES,
        redirect_uri=settings.MICROSOFT_REDIRECT_URI,
    )


def acquire_token(code):

    app = get_msal_app()

    result = app.acquire_token_by_authorization_code(
        code=code,
        scopes=settings.MICROSOFT_SCOPES,
        redirect_uri=settings.MICROSOFT_REDIRECT_URI,
    )

    return result
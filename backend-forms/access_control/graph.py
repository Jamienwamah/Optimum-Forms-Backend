
import msal
import requests

from django.conf import settings


def get_graph_access_token():
    client_id = getattr(settings, "MICROSOFT_CLIENT_ID", None)
    client_secret = getattr(settings, "MICROSOFT_CLIENT_SECRET", None)
    authority = getattr(settings, "MICROSOFT_AUTHORITY", None)

    if not client_id or not client_secret or not authority:
        raise RuntimeError(
            "Microsoft Entra application settings are incomplete."
        )

    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=authority,
    )

    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )

    token = result.get("access_token")

    if not token:
        raise RuntimeError(
            result.get(
                "error_description",
                "Unable to authenticate with Microsoft Graph.",
            )
        )

    return token

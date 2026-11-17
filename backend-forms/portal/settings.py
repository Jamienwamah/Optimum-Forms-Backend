
"""
Django settings for portal project.
"""

from pathlib import Path
import os

from dotenv import load_dotenv


# --------------------------------------------------
# BASE CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in (
        "true", "1", "yes", "on"
    )


def env_list(name, default=""):
    return [
        item.strip()
        for item in os.getenv(name, default).split(",")
        if item.strip()
    ]


# --------------------------------------------------
# SECURITY
# --------------------------------------------------

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    raise ValueError(
        "DJANGO_SECRET_KEY is missing. Configure it in your .env file."
    )

DEBUG = env_bool("DEBUG", False)

ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1"
)


# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "authentication",
    "corsheaders",
    "rest_framework",
    "entraprofile",
    "enclusia",
    "access_control",
    "infrastructure",
    "troubleshoot",
    "replacement",
    "issue",
]


# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# --------------------------------------------------
# CORS AND CSRF
# --------------------------------------------------

CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:4200"
)

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:4200"
)

CORS_ALLOW_CREDENTIALS = True


# --------------------------------------------------
# SESSION AND COOKIE SECURITY
# --------------------------------------------------

SESSION_COOKIE_NAME = "django_session"
SESSION_COOKIE_SAMESITE = os.getenv(
    "SESSION_COOKIE_SAMESITE", "Lax"
)
SESSION_COOKIE_SECURE = env_bool(
    "SESSION_COOKIE_SECURE", not DEBUG
)
SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_SECURE = env_bool(
    "CSRF_COOKIE_SECURE", not DEBUG
)

SECURE_SSL_REDIRECT = env_bool(
    "SECURE_SSL_REDIRECT", False
)


# --------------------------------------------------
# URL CONFIGURATION
# --------------------------------------------------

ROOT_URLCONF = "portal.urls"


# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "portal.wsgi.application"


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# --------------------------------------------------
# DJANGO REST FRAMEWORK
# --------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}


# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# --------------------------------------------------
# MICROSOFT ENTRA ID CONFIGURATION
# --------------------------------------------------

MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID")
GRAPH_SENDER_EMAIL = os.getenv("GRAPH_SENDER_EMAIL")

MICROSOFT_AUTHORITY = (
    f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}"
    if MICROSOFT_TENANT_ID
    else None
)

MICROSOFT_REDIRECT_URI = os.getenv(
    "MICROSOFT_REDIRECT_URI",
    "http://localhost:8000/auth/callback/"
)

MICROSOFT_SCOPES = [
    "User.Read",
    "RoleManagement.Read.Directory",
]

MICROSOFT_DASHBOARD_SUPER_ADMIN_ROLES = [
    "Global Administrator",
]

MICROSOFT_DASHBOARD_ADMIN_ROLES = [
    "User Administrator",
    "Helpdesk Administrator",
    "Service Support Administrator",
]


# --------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

STATIC_URL = "/static/"


# --------------------------------------------------
# EMAIL CONFIGURATION
# --------------------------------------------------

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend"
)

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")


# Compatibility configuration.
# Keep this only if existing application code reads MAILERS.
MAILERS = {
    "default": {
        "BACKEND": EMAIL_BACKEND,
        "OPTIONS": {
            "host": EMAIL_HOST,
            "port": EMAIL_PORT,
            "username": EMAIL_HOST_USER,
            "password": EMAIL_HOST_PASSWORD,
            "use_tls": EMAIL_USE_TLS,
        },
    },
}


# --------------------------------------------------
# APPROVAL EMAIL CONFIGURATION
# --------------------------------------------------

IT_ACCESS_APPROVAL_EMAIL = os.getenv("IT_ACCESS_APPROVAL_EMAIL")
INFRASTRUCTURE_APPROVAL_EMAIL = os.getenv(
    "INFRASTRUCTURE_APPROVAL_EMAIL"
)
DEVICE_REPLACEMENT_APPROVAL_EMAIL = os.getenv(
    "DEVICE_REPLACEMENT_APPROVAL_EMAIL"
)
DEVICE_TROUBLESHOOTING_APPROVAL_EMAIL = os.getenv(
    "DEVICE_TROUBLESHOOTING_APPROVAL_EMAIL"
)
DEVICE_ISSUE_APPROVAL_EMAIL = os.getenv(
    "DEVICE_ISSUE_APPROVAL_EMAIL"
)

INTERNAL_CONTROL_EMAIL = os.getenv("INTERNAL_CONTROL_EMAIL")
IT_ACCESS_DECISION_EMAIL = os.getenv("IT_ACCESS_DECISION_EMAIL")

ACCESS_PORTAL_BASE_URL = os.getenv("ACCESS_PORTAL_BASE_URL")

ACCESS_REQUEST_ADMIN_EMAILS = env_list("ACCESS_REQUEST_ADMIN_EMAILS", [])


# --------------------------------------------------
# AWS SES CONFIGURATION
# --------------------------------------------------

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SES_REGION_NAME = os.getenv("AWS_SES_REGION_NAME")


# --------------------------------------------------
# ACCESS CONTROL GROUPS
# --------------------------------------------------

IT_ACCESS_SUBMITTER_GROUPS = [
    "IT",
    "IT Support",
    "IT Team",
]

# Only these groups are authorized reviewer groups.
APPROVAL_REVIEWER_GROUPS = [
    "Approval Administrators",
    "Internal Control",
]


# --------------------------------------------------
# DEFAULT PRIMARY KEY
# --------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

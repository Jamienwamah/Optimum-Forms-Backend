
from django.conf import settings
from django.db import models


class EnclusiaAccessRequest(models.Model):

    # ==========================================================
    # REQUEST STATUS
    # ==========================================================

    STATUS_CHOICES = [
        ("Submitted", "Submitted"),
        ("In Progress", "In Progress"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Completed", "Completed"),
        ("Closed", "Closed"),
    ]


    # ==========================================================
    # ACCESS EXPIRATION TYPE
    # ==========================================================

    # EXPIRATION_TYPE_CHOICES = [
    #     ("Temporary Request", "Temporary Request"),
    #     ("Permanent Request", "Permanent Request"),
    # ]


    # ==========================================================
    # ENCLUSIA ACCESS REQUIREMENTS
    # ==========================================================

    ACCESS_REQUIRED_CHOICES = [
        (
            "Customer Account and Transaction Management",
            "Customer Account and Transaction Management"
        ),
        (
            "Customer Investment Management",
            "Customer Investment Management"
        ),
        (
            "Portfolio Management",
            "Portfolio Management"
        ),
        (
            "Treasury",
            "Treasury"
        ),
        (
            "Treasury Setup",
            "Treasury Setup"
        ),
        (
            "Investment Module Setup",
            "Investment Module Setup"
        ),
        (
            "Financial Accounting",
            "Financial Accounting"
        ),
        (
            "Financial Accounting Setup",
            "Financial Accounting Setup"
        ),
        (
            "System Administration",
            "System Administration"
        ),
    ]


    # ==========================================================
    # REQUEST INFORMATION
    # ==========================================================

    request_date = models.DateField(
        auto_now_add=True
    )

    requester_name = models.CharField(
        max_length=255
    )


    # ==========================================================
    # PERSON RECEIVING THE ACCESS
    # ==========================================================

    access_for_name = models.CharField(
        max_length=255
    )

    access_for_email = models.EmailField()


    # ==========================================================
    # EMPLOYEE INFORMATION OF REQUESTER
    # ==========================================================

    employee_name = models.CharField(
        max_length=255
    )

    employee_department = models.CharField(
        max_length=255
    )

    employee_job_title = models.CharField(
        max_length=255
    )

    employee_id = models.CharField(
        max_length=100
    )


    # ==========================================================
    # ENCLUSIA CLOUD PLATFORM ACCESS
    # ==========================================================

    # expiration_type = models.CharField(
    #     max_length=50,
    #     choices=EXPIRATION_TYPE_CHOICES
    # )

    access_required = models.CharField(
        max_length=100,
        choices=ACCESS_REQUIRED_CHOICES,
        default="System Administration"
    )

    justification = models.TextField()


    # ==========================================================
    # APPROVAL WORKFLOW
    # ==========================================================

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Submitted"
    )


    # ==========================================================
    # AUTHENTICATED DJANGO USER
    # ==========================================================

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enclusia_access_requests"
    )


    # ==========================================================
    # RECORD TIMESTAMPS
    # ==========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    # ==========================================================
    # MODEL CONFIGURATION
    # ==========================================================

    class Meta:

        ordering = ["-created_at"]

        verbose_name = "Enclusia Access Request"

        verbose_name_plural = "Enclusia Access Requests"


    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __str__(self):

        return (
            f"{self.access_for_name} - "
            f"{self.access_required} - "
            f"{self.status}"
        )

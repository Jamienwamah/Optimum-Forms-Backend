
from django.conf import settings
from django.db import models


class LaptopIssue(models.Model):

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
    # REQUEST INFORMATION
    # ==========================================================

    request_date = models.DateField(
        auto_now_add=True
    )

    document_no = models.CharField(
        max_length=100,
        unique=True
    )

    requester_name = models.CharField(
        max_length=255
    )

    department = models.CharField(
        max_length=255
    )

    job_title = models.CharField(
        max_length=255
    )

    employee_id = models.CharField(
        max_length=100
    )


    # ==========================================================
    # LAPTOP ISSUE INFORMATION
    # ==========================================================

    laptop_details = models.TextField()

    brand_model = models.CharField(
        max_length=255
    )

    serial_number = models.CharField(
        max_length=255
    )

    accessories_provided = models.TextField(
        blank=True
    )

    date_issued = models.DateField()


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
        related_name="laptop_issues"
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

        verbose_name = "Laptop Issue"

        verbose_name_plural = "Laptop Issues"


    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __str__(self):

        return (
            f"{self.document_no} - "
            f"{self.requester_name} - "
            f"{self.status}"
        )

from django.conf import settings
from django.db import models


class EnclusiaAccessRequest(models.Model):

    STATUS_CHOICES = [
        ("Submitted", "Submitted"),
        ("In Progress", "In Progress"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Completed", "Completed"),
        ("Closed", "Closed"),
    ]

    ROLE_CODE_CHOICES = [
        ("ADM", "ADM"),
        ("AO", "AO"),
        ("FIN_DASH", "FIN_DASH"),
        ("FINCON", "FINCON"),
        ("GLOBAL_DASH", "GLOBAL_DASH"),
        ("INT_CTRL", "INT_CTRL"),
        ("INV_SETUP", "INV_SETUP"),
        ("IT_SUP", "IT_SUP"),
        ("OPS", "OPS"),
        ("OPS_DASH", "OPS_DASH"),
        ("SM", "SM"),
        ("TR_OPS", "TR_OPS"),
    ]

    ROLE_CHOICES = [
        ("Administrator", "Administrator"),
        ("Account Officers", "Account Officers"),
        ("Finance Dashboard", "Finance Dashboard"),
        ("Financial Control", "Financial Control"),
        ("Global Dashboard", "Global Dashboard"),
        ("Internal Control", "Internal Control"),
        ("INVESTMENT MODULE SETUP", "INVESTMENT MODULE SETUP"),
        ("IT Support", "IT Support"),
        ("Operations", "Operations"),
        ("OPERATIONS DASHBOARD", "OPERATIONS DASHBOARD"),
        ("Support Manager", "Support Manager"),
        ("TREASURY OPERATIONS", "TREASURY OPERATIONS"),
    ]

    # Request information
    request_date = models.DateField(auto_now_add=True)

    requester_name = models.CharField(
        max_length=255
    )

    # Person receiving the access
    access_for_name = models.CharField(
        max_length=255
    )

    access_for_email = models.EmailField()

    # Employee information of requester
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

    # Enclusia access
    role = models.CharField(
        max_length=100,
        choices=ROLE_CHOICES
    )

    rolecode = models.CharField(
        max_length=50,
        choices=ROLE_CODE_CHOICES
    )

    role_description = models.CharField(
        max_length=255
    )

    reason = models.TextField()

    # Workflow
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Submitted"
    )

    # Django authenticated user who submitted the request
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enclusia_access_requests"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Enclusia Access Request"
        verbose_name_plural = "Enclusia Access Requests"

    def __str__(self):
        return (
            f"{self.access_for_name} - "
            f"{self.rolecode} - "
            f"{self.status}"
        )
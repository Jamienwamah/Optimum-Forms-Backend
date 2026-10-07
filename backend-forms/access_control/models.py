from django.conf import settings
from django.db import models


class ApprovalRequest(models.Model):

    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    # Person who created/submitted the request
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="approval_requests",
    )

    # Person the access/request is actually for
    requested_for_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    requested_for_email = models.EmailField(
        blank=True,
        default="",
    )

    requested_for_department = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    form_code = models.CharField(
        max_length=100
    )

    # Department responsible for approving the request
    department = models.CharField(
        max_length=150
    )

    department_email = models.EmailField()

    reason = models.TextField(
        blank=True,
        default="",
    )

    submission_data = models.JSONField(
        default=dict,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_approval_requests",
    )

    approver_comment = models.TextField(
        blank=True,
        default="",
    )

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return (
            f"{self.form_code} - "
            f"{self.requested_for_name or self.user} - "
            f"{self.status}"
        )
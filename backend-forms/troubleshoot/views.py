
import logging

from django.db import transaction

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from access_control.department_routing import get_approval_department
from access_control.models import ApprovalRequest
from access_control.email import send_approval_request_email

from .serializers import DeviceTroubleshootingSerializer


logger = logging.getLogger(__name__)


class DeviceTroubleshootingCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        logger.info(
            "Device troubleshooting submission started. User ID: %s",
            request.user.id
        )

        # ========================================================
        # VALIDATE DEVICE TROUBLESHOOTING REQUEST
        # ========================================================

        serializer = DeviceTroubleshootingSerializer(
            data=request.data,
            context={"request": request}
        )

        if not serializer.is_valid():

            logger.warning(
                "Device troubleshooting validation failed: %s",
                serializer.errors
            )

            return Response(
                {
                    "success": False,
                    "message": "Please correct the submitted information.",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        company = serializer.validated_data.get("company")

        logger.info(
            "Device troubleshooting validation successful. Company: %s",
            company
        )

        # ========================================================
        # DETERMINE APPROVAL DEPARTMENT
        #
        # Device troubleshooting requests are routed to IT Support
        # through the central department-routing configuration.
        # ========================================================

        try:

            approval = get_approval_department(
                "TROUBLESHOOTING",
                ""
            )

        except ValueError as error:

            logger.exception(
                "Device troubleshooting approval routing failed."
            )

            return Response(
                {
                    "success": False,
                    "message": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(
            "Device troubleshooting approval department determined: %s",
            approval["department"]
        )

        # ========================================================
        # SAVE TROUBLESHOOTING REQUEST AND CREATE APPROVAL
        #
        # Both database records are created in one transaction.
        # If approval creation fails, the troubleshooting request
        # is rolled back as well.
        # ========================================================

        try:

            with transaction.atomic():

                # ====================================================
                # SAVE DEVICE TROUBLESHOOTING REQUEST
                # ====================================================

                troubleshooting_request = serializer.save()

                logger.info(
                    "Device troubleshooting request saved. "
                    "Request ID: %s, Company: %s",
                    troubleshooting_request.id,
                    troubleshooting_request.company
                )

                # ====================================================
                # PREPARE SUBMISSION DETAILS
                # ====================================================

                submission_data = {

                    "request_type": "Device Troubleshooting",

                    "company": troubleshooting_request.company,

                    "requester": {
                        "name": troubleshooting_request.requester_name,
                        "department": troubleshooting_request.department,
                        "job_title": troubleshooting_request.job_title,
                        "employee_id": troubleshooting_request.employee_id,
                    },

                    "device": {
                        "asset_tag": troubleshooting_request.asset_tag or "",
                        "device_type": troubleshooting_request.device_type,
                        "brand_model": troubleshooting_request.brand_model,
                        "serial_number": troubleshooting_request.serial_number,
                        "operating_system":
                            troubleshooting_request.operating_system,
                    },

                    "issue": {
                        "date_reported":
                            troubleshooting_request.date_reported.isoformat()
                            if troubleshooting_request.date_reported
                            else None,

                        "reported_by":
                            troubleshooting_request.reported_by,

                        "description":
                            troubleshooting_request.description,

                        "start_date":
                            troubleshooting_request.start_date.isoformat()
                            if troubleshooting_request.start_date
                            else None,

                        "troubleshooting_attempted":
                            troubleshooting_request.troubleshooting_attempted,

                        "attempted_details":
                            troubleshooting_request.attempted_details or "",
                    },

                    "request_details": {
                        "request_id": troubleshooting_request.id,

                        "company": troubleshooting_request.company,

                        "status": troubleshooting_request.status,

                        "submitted_at":
                            troubleshooting_request.created_at.isoformat()
                            if troubleshooting_request.created_at
                            else None,
                    }
                }

                # ====================================================
                # CREATE CENTRAL APPROVAL REQUEST
                # ====================================================

                approval_request = ApprovalRequest.objects.create(

                    # Authenticated submitting user
                    user=request.user,

                    # Must match central routing configuration
                    form_code="TROUBLESHOOTING",

                    # Determined by get_approval_department()
                    department=approval["department"],

                    department_email=approval["email"],

                    # Approval reason
                    reason=(
                        f"[{troubleshooting_request.company}] "
                        "Device troubleshooting request: "
                        f"{troubleshooting_request.brand_model}"
                    ),

                    # Submitted troubleshooting information
                    submission_data=submission_data
                )

                logger.info(
                    "Device troubleshooting approval request created. "
                    "Approval Request ID: %s, Company: %s",
                    approval_request.id,
                    troubleshooting_request.company
                )

        except Exception:

            logger.exception(
                "Failed to save device troubleshooting request "
                "or create its approval request."
            )

            return Response(
                {
                    "success": False,
                    "message": (
                        "Unable to submit the device troubleshooting request."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ========================================================
        # SEND APPROVAL EMAIL
        #
        # Email is sent after the database transaction commits.
        # Email failure does not delete the submitted records.
        # ========================================================

        email_accepted = False
        email_message_id = None

        try:

            logger.info(
                "Sending device troubleshooting approval notification. "
                "Approval Request ID: %s, Recipient: %s, Company: %s",
                approval_request.id,
                approval_request.department_email,
                troubleshooting_request.company
            )

            email_result = send_approval_request_email(
                approval_request
            )

            logger.info(
                "Device troubleshooting email helper returned: %r",
                email_result
            )

            if isinstance(email_result, dict):

                email_message_id = email_result.get(
                    "MessageId"
                )

            elif isinstance(email_result, str):

                email_message_id = email_result

            if email_message_id:

                email_accepted = True

                logger.info(
                    "Email service accepted device troubleshooting "
                    "approval notification. Message ID: %s",
                    email_message_id
                )

            else:

                logger.warning(
                    "No email MessageId returned for device troubleshooting. "
                    "Approval Request ID: %s",
                    approval_request.id
                )

        except Exception:

            logger.exception(
                "Failed to send device troubleshooting approval email. "
                "Approval Request ID: %s",
                approval_request.id
            )

        # ========================================================
        # RESPONSE
        # ========================================================

        response_data = {

            "success": True,

            "message": (
                "Device troubleshooting request submitted successfully."
            ),

            "company": troubleshooting_request.company,

            "request_id": troubleshooting_request.id,

            "approval_request_id": approval_request.id,

            "department": approval_request.department,

            "approval_status": approval_request.status,

            "email_accepted": email_accepted,

            "email_message_id": email_message_id,

            "request": {
                "company": troubleshooting_request.company,

                "requester": troubleshooting_request.requester_name,

                "device": troubleshooting_request.brand_model,

                "serial_number":
                    troubleshooting_request.serial_number,

                "issue_description":
                    troubleshooting_request.description,

                "status": troubleshooting_request.status,
            }
        }

        logger.info(
            "Device troubleshooting processing completed. "
            "Request ID: %s, Approval Request ID: %s, "
            "Company: %s, Email accepted: %s",
            troubleshooting_request.id,
            approval_request.id,
            troubleshooting_request.company,
            email_accepted
        )

        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )

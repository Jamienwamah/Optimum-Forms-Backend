
import logging

from django.db import transaction

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from access_control.department_routing import get_approval_department
from access_control.models import ApprovalRequest
from access_control.email import send_approval_request_email

from .serializers import DeviceReplacementSerializer


logger = logging.getLogger(__name__)


class DeviceReplacementCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        logger.info(
            "Device replacement submission started. User ID: %s",
            request.user.id
        )

        # ========================================================
        # VALIDATE DEVICE REPLACEMENT REQUEST
        # ========================================================

        serializer = DeviceReplacementSerializer(
            data=request.data,
            context={"request": request}
        )

        if not serializer.is_valid():

            logger.warning(
                "Device replacement validation failed: %s",
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

        logger.info(
            "Device replacement validation successful."
        )

        # ========================================================
        # DETERMINE APPROVAL DEPARTMENT
        #
        # Device replacement requests are routed to IT Support
        # through the central department-routing configuration.
        # ========================================================

        try:

            approval = get_approval_department(
                "REPLACEMENT",
                ""
            )

        except ValueError as error:

            logger.exception(
                "Device replacement approval routing failed."
            )

            return Response(
                {
                    "success": False,
                    "message": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(
            "Device replacement approval department determined: %s",
            approval["department"]
        )

        # ========================================================
        # SAVE REPLACEMENT REQUEST AND CREATE APPROVAL REQUEST
        #
        # Both records are created in one database transaction.
        # If approval creation fails, the replacement request
        # is rolled back as well.
        # ========================================================

        try:

            with transaction.atomic():

                # ====================================================
                # SAVE DEVICE REPLACEMENT REQUEST
                # ====================================================

                replacement_request = serializer.save()

                logger.info(
                    "Device replacement request saved. Request ID: %s",
                    replacement_request.id
                )

                # ====================================================
                # PREPARE SUBMISSION DETAILS
                # ====================================================

                submission_data = {

                    "request_type": "Device Replacement",

                    "requester": {
                        "name": replacement_request.requester_name,
                        "department": replacement_request.department,
                        "job_title": replacement_request.job_title,
                        "employee_id": replacement_request.employee_id,
                    },

                    "current_device": {
                        "asset_tag": replacement_request.asset_tag or "",
                        "device_type": replacement_request.device_type,
                        "brand_model": replacement_request.brand_model,
                        "serial_number": replacement_request.serial_number,
                        "reason_for_replacement":
                            replacement_request.reason_for_replacement,
                    },

                    "replacement_details": {
                        "requested_device_type":
                            replacement_request.requested_device_type,

                        "urgency_level":
                            replacement_request.urgency_level,

                        "justification":
                            replacement_request.justification,

                        "required_date":
                            replacement_request.required_date.isoformat()
                            if replacement_request.required_date
                            else None,
                    },

                    "request_details": {
                        "request_id": replacement_request.id,
                        "status": replacement_request.status,

                        "submitted_at":
                            replacement_request.created_at.isoformat()
                            if replacement_request.created_at
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
                    form_code="REPLACEMENT",

                    # Determined by get_approval_department()
                    department=approval["department"],

                    department_email=approval["email"],

                    # Approval reason
                    reason=(
                        "Device replacement approval required: "
                        f"{replacement_request.brand_model}"
                    ),

                    # Submitted replacement information
                    submission_data=submission_data
                )

                logger.info(
                    "Device replacement approval request created. "
                    "Approval Request ID: %s",
                    approval_request.id
                )

        except Exception:

            logger.exception(
                "Failed to save device replacement request "
                "or create its approval request."
            )

            return Response(
                {
                    "success": False,
                    "message": (
                        "Unable to submit the device replacement request."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ========================================================
        # SEND APPROVAL EMAIL
        #
        # The database transaction has already committed.
        # Email failure will not remove the submitted records.
        # ========================================================

        email_accepted = False
        email_message_id = None

        try:

            logger.info(
                "Sending device replacement approval notification. "
                "Approval Request ID: %s, Recipient: %s",
                approval_request.id,
                approval_request.department_email
            )

            email_result = send_approval_request_email(
                approval_request
            )

            logger.info(
                "Device replacement email helper returned: %r",
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
                    "Email service accepted device replacement "
                    "approval notification. Message ID: %s",
                    email_message_id
                )

            else:

                logger.warning(
                    "No email MessageId returned for device replacement. "
                    "Approval Request ID: %s",
                    approval_request.id
                )

        except Exception:

            logger.exception(
                "Failed to send device replacement approval email. "
                "Approval Request ID: %s",
                approval_request.id
            )

        # ========================================================
        # RESPONSE
        # ========================================================

        response_data = {

            "success": True,

            "message": (
                "Device replacement request submitted successfully."
            ),

            "request_id": replacement_request.id,

            "approval_request_id": approval_request.id,

            "department": approval_request.department,

            "approval_status": approval_request.status,

            "email_accepted": email_accepted,

            "email_message_id": email_message_id,

            "request": {
                "requester": replacement_request.requester_name,

                "device": replacement_request.brand_model,

                "serial_number": replacement_request.serial_number,

                "requested_device_type":
                    replacement_request.requested_device_type,

                "urgency_level":
                    replacement_request.urgency_level,

                "status": replacement_request.status,
            }
        }

        logger.info(
            "Device replacement processing completed. "
            "Request ID: %s, Approval Request ID: %s, "
            "Email accepted: %s",
            replacement_request.id,
            approval_request.id,
            email_accepted
        )

        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )

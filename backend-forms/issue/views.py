
import logging

from django.db import transaction

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from access_control.department_routing import get_approval_department
from access_control.email import send_approval_request_email
from access_control.models import ApprovalRequest

from .serializers import LaptopIssueSerializer


logger = logging.getLogger(__name__)


class LaptopIssueCreateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        logger.info(
            "Laptop issue submission started. User ID: %s",
            request.user.id
        )

        # ========================================================
        # VALIDATE LAPTOP ISSUE
        # ========================================================

        serializer = LaptopIssueSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        if not serializer.is_valid():

            logger.warning(
                "Laptop issue validation failed: %s",
                serializer.errors
            )

            return Response(
                {
                    "message": "Validation failed.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(
            "Laptop issue validation successful."
        )

        # ========================================================
        # GET COMPANY
        # ========================================================

        company = serializer.validated_data.get(
            "company"
        )

        logger.info(
            "Laptop issue company identified: %s",
            company
        )

        # ========================================================
        # DETERMINE APPROVAL DEPARTMENT
        # ========================================================

        try:

            approval = get_approval_department(
                "ISSUE",
                ""
            )

        except ValueError as error:

            logger.exception(
                "Laptop issue approval routing failed."
            )

            return Response(
                {
                    "message": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(
            "Laptop issue approval department determined: %s",
            approval["department"]
        )

        # ========================================================
        # SAVE LAPTOP ISSUE AND CREATE APPROVAL
        # ========================================================

        try:

            with transaction.atomic():

                laptop_issue = serializer.save()

                logger.info(
                    "Laptop issue saved. Record ID: %s, Company: %s",
                    laptop_issue.id,
                    laptop_issue.company
                )

                # ====================================================
                # BUILD APPROVAL SUBMISSION DATA
                # ====================================================

                submission_data = {

                    "company": laptop_issue.company,

                    "documentNo": laptop_issue.document_no,

                    "requestDate": str(
                        laptop_issue.request_date
                    ),

                    "employee": {

                        "name": laptop_issue.requester_name,

                        "department": laptop_issue.department,

                        "jobTitle": laptop_issue.job_title,

                        "employeeId": laptop_issue.employee_id,

                        "email": request.user.email
                    },

                    "officialUse": {

                        "laptopDetails": laptop_issue.laptop_details,

                        "brandModel": laptop_issue.brand_model,

                        "serialNumber": laptop_issue.serial_number,

                        "accessoriesProvided": (
                            laptop_issue.accessories_provided or ""
                        ),

                        "dateIssued": str(
                            laptop_issue.date_issued
                        )
                    }
                }

                # ====================================================
                # CREATE CENTRAL APPROVAL REQUEST
                # ====================================================

                approval_request = ApprovalRequest.objects.create(

                    user=request.user,

                    form_code="ISSUE",

                    department=approval["department"],

                    department_email=approval["email"],

                    reason=(
                        "Laptop issue approval required: "
                        f"{laptop_issue.document_no} "
                        f"({laptop_issue.company})"
                    ),

                    submission_data=submission_data,
                )

                logger.info(
                    "Laptop issue approval request created. "
                    "Approval Request ID: %s, Company: %s",
                    approval_request.id,
                    laptop_issue.company
                )

        except Exception:

            logger.exception(
                "Failed to save laptop issue or create approval request."
            )

            return Response(
                {
                    "message": (
                        "The laptop issue could not be submitted. "
                        "Please try again or contact IT."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ========================================================
        # SEND APPROVAL EMAIL
        # ========================================================

        email_accepted = False
        email_message_id = None

        try:

            logger.info(
                "Sending laptop issue approval notification. "
                "Approval Request ID: %s, Recipient: %s, Company: %s",
                approval_request.id,
                approval_request.department_email,
                laptop_issue.company
            )

            email_result = send_approval_request_email(
                approval_request
            )

            logger.info(
                "Laptop issue email helper returned: %r",
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
                    "Email service accepted laptop issue approval "
                    "notification. Message ID: %s",
                    email_message_id
                )

            else:

                logger.warning(
                    "Laptop issue approval email returned no message ID. "
                    "Approval Request ID: %s",
                    approval_request.id
                )

        except Exception:

            logger.exception(
                "Failed to send laptop issue approval email. "
                "Approval Request ID: %s",
                approval_request.id
            )

        # ========================================================
        # RESPONSE
        # ========================================================

        response_data = {

            "message": (
                "Laptop issue submitted successfully."
            ),

            "id": laptop_issue.id,

            "company": laptop_issue.company,

            "document_no": laptop_issue.document_no,

            "approval_request_id": approval_request.id,

            "approval_department": approval_request.department,

            "approval_status": approval_request.status,

            "email_accepted": email_accepted,

            "email_message_id": email_message_id,

            "requester": {

                "name": laptop_issue.requester_name,

                "email": request.user.email
            },

            "request_date": laptop_issue.request_date
        }

        logger.info(
            "Laptop issue processing completed. "
            "Record ID: %s, Approval Request ID: %s, "
            "Company: %s, Email accepted: %s",
            laptop_issue.id,
            approval_request.id,
            laptop_issue.company,
            email_accepted
        )

        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )

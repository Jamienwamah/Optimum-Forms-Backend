
import logging

from django.db import transaction

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from access_control.department_routing import get_approval_department
from access_control.email import send_approval_request_email
from access_control.models import ApprovalRequest

from .serializers import InfrastructureReceiptSerializer


logger = logging.getLogger(__name__)


class InfrastructureReceiptCreateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        logger.info(
            "Infrastructure receipt submission started. User ID: %s",
            request.user.id
        )

        # ========================================================
        # VALIDATE INFRASTRUCTURE RECEIPT
        # ========================================================

        serializer = InfrastructureReceiptSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        if not serializer.is_valid():

            logger.warning(
                "Infrastructure receipt validation failed: %s",
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
            "Infrastructure receipt validation successful."
        )

        # ========================================================
        # DETERMINE APPROVAL DEPARTMENT
        #
        # Infrastructure receipts are routed through the
        # central department-routing configuration.
        # ========================================================

        try:

            approval = get_approval_department(
                "INFRASTRUCTURE",
                ""
            )

        except ValueError as error:

            logger.exception(
                "Infrastructure approval routing failed."
            )

            return Response(
                {
                    "message": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(
            "Infrastructure approval department determined: %s",
            approval["department"]
        )

        # ========================================================
        # SAVE INFRASTRUCTURE RECEIPT AND CREATE APPROVAL
        #
        # Both database records are created in one transaction.
        # If approval creation fails, the receipt is rolled back.
        # ========================================================

        try:

            with transaction.atomic():

                infrastructure_receipt = serializer.save()

                logger.info(
                    "Infrastructure receipt saved. Receipt ID: %s",
                    infrastructure_receipt.id
                )

                # ====================================================
                # BUILD APPROVAL SUBMISSION DATA
                # ====================================================

                submission_data = {

                    "documentNo": infrastructure_receipt.document_no,

                    "dateReceived": str(
                        infrastructure_receipt.date_received
                    ),

                    "requester": {
                        "name": infrastructure_receipt.requester_name,
                        "email": request.user.email
                    },

                    "procurement": {
                        "assetTag": infrastructure_receipt.asset_tag or "",
                        "poNumber": infrastructure_receipt.po_number,
                        "invoiceNumber": infrastructure_receipt.invoice_number,
                        "vendorSupplier": infrastructure_receipt.vendor_supplier,
                        "deliveryNoteNumber": infrastructure_receipt.delivery_note_number,
                        "procuredBy": infrastructure_receipt.procured_by,
                        "fundingSource": infrastructure_receipt.funding_source or ""
                    },

                    "infrastructure": {
                        "category": infrastructure_receipt.category,
                        "brandModel": infrastructure_receipt.brand_model,
                        "serialNumber": infrastructure_receipt.serial_number,
                        "quantity": infrastructure_receipt.quantity,
                        "specifications": infrastructure_receipt.specifications or ""
                    },

                    "inspection": {
                        "physicalCondition": infrastructure_receipt.physical_condition,
                        "accessoriesIncluded": infrastructure_receipt.accessories_included,
                        "passedInspection": infrastructure_receipt.passed_inspection,
                        "inspectedBy": infrastructure_receipt.inspected_by,
                        "inspectionDate": str(
                            infrastructure_receipt.inspection_date
                        ),
                        "notes": infrastructure_receipt.notes or ""
                    }
                }

                # ====================================================
                # CREATE CENTRAL APPROVAL REQUEST
                # ====================================================

                approval_request = ApprovalRequest.objects.create(

                    # Authenticated user submitting the request
                    user=request.user,

                    # Must match the central routing configuration
                    form_code="INFRASTRUCTURE",

                    # Determined by get_approval_department()
                    department=approval["department"],

                    department_email=approval["email"],

                    # Approval reason
                    reason=(
                        "Infrastructure receipt approval required: "
                        f"{infrastructure_receipt.document_no}"
                    ),

                    # Submitted infrastructure information
                    submission_data=submission_data,
                )

                logger.info(
                    "Infrastructure approval request created. "
                    "Approval Request ID: %s",
                    approval_request.id
                )

        except Exception:

            logger.exception(
                "Failed to save infrastructure receipt or create "
                "its approval request."
            )

            return Response(
                {
                    "message": (
                        "The infrastructure receipt could not be "
                        "submitted. Please try again or contact IT."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ========================================================
        # SEND APPROVAL EMAIL
        #
        # Email is sent after the database transaction commits.
        # An email failure does not delete the submitted records.
        # ========================================================

        email_accepted = False
        email_message_id = None

        try:

            logger.info(
                "Sending infrastructure approval notification. "
                "Approval Request ID: %s, Recipient: %s",
                approval_request.id,
                approval_request.department_email
            )

            email_result = send_approval_request_email(
                approval_request
            )

            logger.info(
                "Infrastructure email helper returned: %r",
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
                    "Email service accepted infrastructure approval "
                    "notification. Message ID: %s",
                    email_message_id
                )

            else:

                logger.warning(
                    "Infrastructure approval email helper returned "
                    "no message ID. Approval Request ID: %s",
                    approval_request.id
                )

        except Exception:

            logger.exception(
                "Failed to send infrastructure approval email. "
                "Approval Request ID: %s",
                approval_request.id
            )

        # ========================================================
        # RESPONSE
        # ========================================================

        response_data = {

            "message": (
                "Infrastructure receipt submitted successfully."
            ),

            "id": infrastructure_receipt.id,

            "approval_request_id": approval_request.id,

            "approval_department": approval_request.department,

            "approval_status": approval_request.status,

            "email_accepted": email_accepted,

            "email_message_id": email_message_id,

            "document_no": infrastructure_receipt.document_no,

            "requester": {
                "name": infrastructure_receipt.requester_name,
                "email": request.user.email
            },

            "request_date": infrastructure_receipt.request_date
        }

        logger.info(
            "Infrastructure receipt processing completed. "
            "Receipt ID: %s, Approval Request ID: %s, "
            "Email accepted: %s",
            infrastructure_receipt.id,
            approval_request.id,
            email_accepted
        )

        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )

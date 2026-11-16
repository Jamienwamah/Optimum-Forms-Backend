
# import logging

# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from access_control.department_routing import get_approval_department
# from access_control.email import send_approval_request_email
# from access_control.models import ApprovalRequest

# from .serializers import EnclusiaAccessRequestSerializer


# logger = logging.getLogger(__name__)


# class EnclusiaAccessRequestCreateView(APIView):

#     permission_classes = [
#         IsAuthenticated
#     ]

#     def post(self, request):

#         # ========================================================
#         # VALIDATE ENCLUSIA ACCESS REQUEST
#         # ========================================================

#         serializer = EnclusiaAccessRequestSerializer(
#             data=request.data,
#             context={
#                 "request": request
#             }
#         )

#         if not serializer.is_valid():

#             return Response(
#                 {
#                     "message": "Validation failed.",
#                     "errors": serializer.errors,
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # ========================================================
#         # SAVE ENCLUSIA REQUEST
#         #
#         # The serializer verifies the accessFor employee
#         # against Microsoft Entra.
#         # ========================================================

#         access_request = serializer.save()

#         # ========================================================
#         # GET VERIFIED ACCESS-FOR EMPLOYEE
#         # ========================================================

#         verified_access_for = getattr(
#             access_request,
#             "verified_access_for",
#             None
#         )

#         if not verified_access_for:

#             logger.error(
#                 "Verified access-for employee missing for Enclusia request ID: %s",
#                 access_request.id
#             )

#             return Response(
#                 {
#                     "message": (
#                         "Unable to verify the employee "
#                         "receiving the requested access."
#                     )
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # ========================================================
#         # GET VERIFIED REQUESTER
#         # ========================================================

#         verified_requester = getattr(
#             access_request,
#             "verified_requester",
#             None
#         )

#         if not verified_requester:

#             logger.error(
#                 "Verified requester missing for Enclusia request ID: %s",
#                 access_request.id
#             )

#             return Response(
#                 {
#                     "message": (
#                         "Unable to determine the person "
#                         "creating this request."
#                     )
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # ========================================================
#         # DETERMINE APPROVAL DEPARTMENT
#         #
#         # Routing is based on the ACCESS-FOR employee's
#         # verified Microsoft Entra department.
#         # ========================================================

#         employee_department = (
#             verified_access_for.get("department") or ""
#         ).strip()

#         if not employee_department:

#             return Response(
#                 {
#                     "message": (
#                         "Unable to determine the department "
#                         "of the employee receiving access."
#                     )
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:

#             approval = get_approval_department(
#                 "OST-ENCLUSIA-ACCESS",
#                 employee_department
#             )

#         except ValueError as error:

#             logger.exception(
#                 "Department routing failed for Enclusia request."
#             )

#             return Response(
#                 {
#                     "message": str(error)
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # ========================================================
#         # BUILD VERIFIED SUBMISSION DATA
#         # ========================================================

#         submission_data = dict(
#             request.data
#         )

#         submission_data["verifiedAccessFor"] = {
#             "name": verified_access_for.get("name", ""),
#             "email": verified_access_for.get("email", ""),
#             "department": verified_access_for.get("department", ""),
#             "jobTitle": verified_access_for.get("jobTitle", ""),
#             "employeeId": verified_access_for.get("employeeId", ""),
#             "entraObjectId": verified_access_for.get("id", "")
#         }

#         submission_data["verifiedRequester"] = {
#             "name": verified_requester.get("name", ""),
#             "email": verified_requester.get("email", ""),
#             "department": verified_requester.get("department", ""),
#             "jobTitle": verified_requester.get("jobTitle", ""),
#             "employeeId": verified_requester.get("employeeId", "")
#         }

#         # ========================================================
#         # CREATE APPROVAL REQUEST
#         # ========================================================

#         justification = (
#             request.data
#             .get("enclusiaAccess", {})
#             .get("justification", "")
#         )

#         approval_request = ApprovalRequest.objects.create(

#             # Person creating the request
#             user=request.user,

#             # Form identifier
#             form_code="OST-ENCLUSIA-ACCESS",

#             # Department receiving the approval
#             department=approval["department"],

#             department_email=approval["email"],

#             # User-provided justification
#             reason=justification,

#             # Original and verified submission information
#             submission_data=submission_data,
#         )

#         logger.info(
#             "Enclusia approval request created successfully. "
#             "Approval Request ID: %s",
#             approval_request.id
#         )

#         # ========================================================
#         # SEND APPROVAL EMAIL
#         # ========================================================

#         email_sent = False

#         try:

#             send_approval_request_email(
#                 approval_request
#             )

#             email_sent = True

#             logger.info(
#                 "Enclusia approval email sent successfully. "
#                 "Approval Request ID: %s",
#                 approval_request.id
#             )

#         except Exception:

#             logger.exception(
#                 "Failed to send Enclusia approval email. "
#                 "Approval Request ID: %s",
#                 approval_request.id
#             )

#         # ========================================================
#         # RESPONSE
#         # ========================================================

#         return Response(
#             {
#                 "message": (
#                     "Enclusia Cloud Platform "
#                     "access request submitted successfully."
#                 ),

#                 "id": access_request.id,

#                 "approval_request_id": approval_request.id,

#                 "approval_department": approval_request.department,

#                 "approval_status": approval_request.status,

#                 "email_sent": email_sent,

#                 "access_for": {
#                     "name": verified_access_for.get("name", ""),
#                     "email": verified_access_for.get("email", ""),
#                     "department": verified_access_for.get("department", "")
#                 },

#                 "requester": {
#                     "name": verified_requester.get("name", ""),
#                     "email": verified_requester.get("email", "")
#                 },

#                 "request_date": access_request.request_date,
#             },

#             status=status.HTTP_201_CREATED
#         )



import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from access_control.department_routing import get_approval_department
from access_control.email import send_approval_request_email
from access_control.models import ApprovalRequest

from .serializers import EnclusiaAccessRequestSerializer


logger = logging.getLogger(__name__)


class EnclusiaAccessRequestCreateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        print("\n========== ENCLUSIA ACCESS REQUEST ==========")

        # ========================================================
        # VALIDATE ENCLUSIA ACCESS REQUEST
        # ========================================================

        serializer = EnclusiaAccessRequestSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        if not serializer.is_valid():

            print("VALIDATION FAILED:")
            print(serializer.errors)

            return Response(
                {
                    "message": "Validation failed.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        print("Validation successful.")

        # ========================================================
        # SAVE ENCLUSIA REQUEST
        # ========================================================

        access_request = serializer.save()

        print(
            "Enclusia access request saved. "
            f"Request ID: {access_request.id}"
        )

        # ========================================================
        # GET VERIFIED ACCESS-FOR EMPLOYEE
        # ========================================================

        verified_access_for = getattr(
            access_request,
            "verified_access_for",
            None
        )

        if not verified_access_for:

            print("ERROR: Verified access-for employee is missing.")

            return Response(
                {
                    "message": (
                        "Unable to verify the employee "
                        "receiving the requested access."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ========================================================
        # GET VERIFIED REQUESTER
        # ========================================================

        verified_requester = getattr(
            access_request,
            "verified_requester",
            None
        )

        if not verified_requester:

            print("ERROR: Verified requester is missing.")

            return Response(
                {
                    "message": (
                        "Unable to determine the person "
                        "creating this request."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ========================================================
        # DETERMINE APPROVAL DEPARTMENT
        # ========================================================

        employee_department = (
            verified_access_for.get("department") or ""
        ).strip()

        if not employee_department:

            print("ERROR: Employee department is missing.")

            return Response(
                {
                    "message": (
                        "Unable to determine the department "
                        "of the employee receiving access."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            approval = get_approval_department(
                "ENCLUSIA-ACCESS",
                employee_department
            )

            print(
                "Approval department determined: "
                f"{approval['department']}"
            )

        except ValueError as error:

            logger.exception(
                "Department routing failed for Enclusia request."
            )

            print(f"DEPARTMENT ROUTING ERROR: {error}")

            return Response(
                {
                    "message": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ========================================================
        # BUILD VERIFIED SUBMISSION DATA
        # ========================================================

        submission_data = dict(request.data)

        submission_data["verifiedAccessFor"] = {
            "name": verified_access_for.get("name", ""),
            "email": verified_access_for.get("email", ""),
            "department": verified_access_for.get("department", ""),
            "jobTitle": verified_access_for.get("jobTitle", ""),
            "employeeId": verified_access_for.get("employeeId", ""),
            "entraObjectId": verified_access_for.get("id", "")
        }

        submission_data["verifiedRequester"] = {
            "name": verified_requester.get("name", ""),
            "email": verified_requester.get("email", ""),
            "department": verified_requester.get("department", ""),
            "jobTitle": verified_requester.get("jobTitle", ""),
            "employeeId": verified_requester.get("employeeId", "")
        }

        # ========================================================
        # CREATE APPROVAL REQUEST
        # ========================================================

        justification = (
            request.data
            .get("enclusiaAccess", {})
            .get("justification", "")
        )

        approval_request = ApprovalRequest.objects.create(

            user=request.user,

            form_code="ENCLUSIA-ACCESS",

            department=approval["department"],

            department_email=approval["email"],

            reason=justification,

            submission_data=submission_data,
        )

        print(
            "Approval request created successfully. "
            f"Approval Request ID: {approval_request.id}"
        )

        print(
            f"Approval Department: {approval_request.department}"
        )

        print(
            f"Approval Department Email: "
            f"{approval_request.department_email}"
        )

        # ========================================================
        # SEND APPROVAL EMAIL
        # ========================================================

        email_sent = False
        email_message_id = None

        print("\n========== ENCLUSIA EMAIL DEBUG ==========")

        print(
            "Attempting to send approval email for "
            f"Approval Request ID: {approval_request.id}"
        )

        try:

            print(
                "Calling send_approval_request_email()..."
            )

            email_result = send_approval_request_email(
                approval_request
            )

            print(
                "Email function returned successfully."
            )

            print(
                f"Email function result: {email_result!r}"
            )

            if isinstance(email_result, dict):

                email_message_id = email_result.get(
                    "MessageId"
                )

            elif isinstance(email_result, str):

                email_message_id = email_result

            if email_message_id:

                email_sent = True

                print(
                    "SUCCESS: Amazon SES accepted the email."
                )

                print(
                    f"SES Message ID: {email_message_id}"
                )

            else:

                print(
                    "WARNING: No SES MessageId was returned."
                )

                print(
                    "The email function may not be returning "
                    "the SES response."
                )

        except Exception as error:

            print("\nEMAIL SENDING FAILED!")

            print(
                f"Error type: {type(error).__name__}"
            )

            print(
                f"Error details: {error}"
            )

            logger.exception(
                "Failed to send Enclusia approval email. "
                "Approval Request ID: %s",
                approval_request.id
            )

        finally:

            print("========== END EMAIL DEBUG ==========\n")

        # ========================================================
        # RESPONSE
        # ========================================================

        response_data = {
            "message": (
                "Enclusia Cloud Platform "
                "access request submitted successfully."
            ),

            "id": access_request.id,

            "approval_request_id": approval_request.id,

            "approval_department": approval_request.department,

            "approval_status": approval_request.status,

            "email_sent": email_sent,

            "email_message_id": email_message_id,

            "access_for": {
                "name": verified_access_for.get("name", ""),
                "email": verified_access_for.get("email", ""),
                "department": verified_access_for.get("department", "")
            },

            "requester": {
                "name": verified_requester.get("name", ""),
                "email": verified_requester.get("email", "")
            },

            "request_date": access_request.request_date,
        }

        print(
            "Enclusia access request processing completed."
        )

        print("============================================\n")

        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )

from rest_framework import serializers

from .models import InfrastructureReceipt


# ==========================================================
# PROCUREMENT INFORMATION SERIALIZER
# ==========================================================

class ProcurementSerializer(serializers.Serializer):

    assetTag = serializers.CharField(
        required=False,
        allow_blank=True
    )

    poNumber = serializers.CharField(
        required=True
    )

    invoiceNumber = serializers.CharField(
        required=True
    )

    vendorSupplier = serializers.CharField(
        required=True
    )

    deliveryNoteNumber = serializers.CharField(
        required=True
    )

    procuredBy = serializers.CharField(
        required=True
    )

    fundingSource = serializers.CharField(
        required=False,
        allow_blank=True
    )


# ==========================================================
# INFRASTRUCTURE INFORMATION SERIALIZER
# ==========================================================

class InfrastructureSerializer(serializers.Serializer):

    category = serializers.ChoiceField(
        choices=[
            choice[0]
            for choice in InfrastructureReceipt.CATEGORY_CHOICES
        ]
    )

    brandModel = serializers.CharField(
        required=True
    )

    serialNumber = serializers.CharField(
        required=True
    )

    quantity = serializers.IntegerField(
        required=True,
        min_value=1
    )

    specifications = serializers.CharField(
        required=False,
        allow_blank=True
    )


# ==========================================================
# INSPECTION INFORMATION SERIALIZER
# ==========================================================

class InspectionSerializer(serializers.Serializer):

    physicalCondition = serializers.ChoiceField(
        choices=[
            choice[0]
            for choice in InfrastructureReceipt.PHYSICAL_CONDITION_CHOICES
        ]
    )

    accessoriesIncluded = serializers.BooleanField(
        required=True
    )

    passedInspection = serializers.BooleanField(
        required=True
    )

    inspectedBy = serializers.CharField(
        required=True
    )

    inspectionDate = serializers.DateField(
        required=True
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True
    )


# ==========================================================
# MAIN INFRASTRUCTURE RECEIPT SERIALIZER
# ==========================================================

class InfrastructureReceiptSerializer(serializers.Serializer):

    # ------------------------------------------------------
    # CURRENT DATE
    # ------------------------------------------------------

    currentDate = serializers.DateField(
        required=False,
        write_only=True
    )


    # ------------------------------------------------------
    # DOCUMENT INFORMATION
    # ------------------------------------------------------

    documentNo = serializers.CharField(
        required=True
    )

    dateReceived = serializers.DateField(
        required=True
    )


    # ------------------------------------------------------
    # PROCUREMENT INFORMATION
    # ------------------------------------------------------

    procurement = ProcurementSerializer(
        required=True
    )


    # ------------------------------------------------------
    # INFRASTRUCTURE INFORMATION
    # ------------------------------------------------------

    infrastructure = InfrastructureSerializer(
        required=True
    )


    # ------------------------------------------------------
    # INSPECTION INFORMATION
    # ------------------------------------------------------

    inspection = InspectionSerializer(
        required=True
    )


    # ======================================================
    # CREATE INFRASTRUCTURE RECEIPT
    # ======================================================

    def create(self, validated_data):

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:

            raise serializers.ValidationError(
                {
                    "requester": (
                        "You must be authenticated to submit "
                        "an infrastructure receipt."
                    )
                }
            )


        # --------------------------------------------------
        # GET AUTHENTICATED REQUESTER
        # --------------------------------------------------

        requester_name = (
            request.user.get_full_name()
            or request.user.get_username()
        ).strip()


        # --------------------------------------------------
        # REMOVE CURRENT DATE
        # --------------------------------------------------

        validated_data.pop(
            "currentDate",
            None
        )


        # --------------------------------------------------
        # REMOVE NESTED DATA
        # --------------------------------------------------

        procurement_data = validated_data.pop(
            "procurement"
        )

        infrastructure_data = validated_data.pop(
            "infrastructure"
        )

        inspection_data = validated_data.pop(
            "inspection"
        )


        # --------------------------------------------------
        # CREATE DATABASE RECORD
        # --------------------------------------------------

        infrastructure_receipt = InfrastructureReceipt.objects.create(

            # ----------------------------------------------
            # AUTHENTICATED REQUESTER
            # ----------------------------------------------

            created_by=request.user,

            requester_name=requester_name,


            # ----------------------------------------------
            # DOCUMENT INFORMATION
            # ----------------------------------------------

            document_no=validated_data.get(
                "documentNo"
            ),

            date_received=validated_data.get(
                "dateReceived"
            ),


            # ----------------------------------------------
            # PROCUREMENT INFORMATION
            # ----------------------------------------------

            asset_tag=procurement_data.get(
                "assetTag",
                ""
            ),

            po_number=procurement_data.get(
                "poNumber"
            ),

            invoice_number=procurement_data.get(
                "invoiceNumber"
            ),

            vendor_supplier=procurement_data.get(
                "vendorSupplier"
            ),

            delivery_note_number=procurement_data.get(
                "deliveryNoteNumber"
            ),

            procured_by=procurement_data.get(
                "procuredBy"
            ),

            funding_source=procurement_data.get(
                "fundingSource",
                ""
            ),


            # ----------------------------------------------
            # INFRASTRUCTURE INFORMATION
            # ----------------------------------------------

            category=infrastructure_data.get(
                "category"
            ),

            brand_model=infrastructure_data.get(
                "brandModel"
            ),

            serial_number=infrastructure_data.get(
                "serialNumber"
            ),

            quantity=infrastructure_data.get(
                "quantity"
            ),

            specifications=infrastructure_data.get(
                "specifications",
                ""
            ),


            # ----------------------------------------------
            # INSPECTION INFORMATION
            # ----------------------------------------------

            physical_condition=inspection_data.get(
                "physicalCondition"
            ),

            accessories_included=inspection_data.get(
                "accessoriesIncluded"
            ),

            passed_inspection=inspection_data.get(
                "passedInspection"
            ),

            inspected_by=inspection_data.get(
                "inspectedBy"
            ),

            inspection_date=inspection_data.get(
                "inspectionDate"
            ),

            notes=inspection_data.get(
                "notes",
                ""
            )

        )


        return infrastructure_receipt
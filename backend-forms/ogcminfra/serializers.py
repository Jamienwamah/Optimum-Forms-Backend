from rest_framework import serializers

from .models import OGCMInfrastructureReceipt


class EmployeeSerializer(serializers.Serializer):

    name = serializers.CharField(
        required=False,
        allow_blank=True
    )

    department = serializers.CharField(
        required=False,
        allow_blank=True
    )

    jobTitle = serializers.CharField(
        required=False,
        allow_blank=True
    )

    employeeId = serializers.CharField(
        required=False,
        allow_blank=True
    )


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


class InfrastructureSerializer(serializers.Serializer):

    category = serializers.CharField(
        required=True
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


class InspectionSerializer(serializers.Serializer):

    physicalCondition = serializers.CharField(
        required=True
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


class OGCMInfrastructureReceiptSerializer(serializers.Serializer):

    # Sent by Angular but not stored directly in the model.
    currentDate = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True
    )

    employee = EmployeeSerializer(
        required=False
    )

    documentNo = serializers.CharField(
        required=True
    )

    dateReceived = serializers.DateField(
        required=True
    )

    procurement = ProcurementSerializer(
        required=True
    )

    infrastructure = InfrastructureSerializer(
        required=True
    )

    inspection = InspectionSerializer(
        required=True
    )

    def create(self, validated_data):

        request = self.context["request"]

        # ----------------------------------------------------
        # GET THE LOGGED-IN USER'S ENTRA PROFILE
        # ----------------------------------------------------

        profile = getattr(
            request.user,
            "entra_profile",
            None
        )

        if not profile:
            raise serializers.ValidationError(
                {
                    "employee": (
                        "Microsoft Entra profile not found "
                        "for this user."
                    )
                }
            )

        # ----------------------------------------------------
        # REMOVE NESTED DATA
        # ----------------------------------------------------

        employee_data = validated_data.pop(
            "employee",
            {}
        )

        procurement_data = validated_data.pop(
            "procurement"
        )

        infrastructure_data = validated_data.pop(
            "infrastructure"
        )

        inspection_data = validated_data.pop(
            "inspection"
        )

        # currentDate is intentionally not stored.
        validated_data.pop(
            "currentDate",
            None
        )

        # ----------------------------------------------------
        # EMPLOYEE INFORMATION
        #
        # Name, department and job title come from Entra.
        # Employee ID comes from the Angular form.
        # ----------------------------------------------------

        employee_id = employee_data.get(
            "employeeId",
            ""
        )

        # ----------------------------------------------------
        # CREATE DATABASE RECORD
        # ----------------------------------------------------

        infrastructure = OGCMInfrastructureReceipt.objects.create(

            # -----------------------------------------------
            # Document
            # -----------------------------------------------

            document_no=validated_data.get(
                "documentNo"
            ),

            date_received=validated_data.get(
                "dateReceived"
            ),

            # -----------------------------------------------
            # Authenticated User
            # -----------------------------------------------

            created_by=request.user,

            # -----------------------------------------------
            # Employee Information
            # -----------------------------------------------

            employee_name=profile.display_name or "",

            employee_id=employee_id,

            employee_department=profile.department or "",

            employee_job_title=profile.job_title or "",

            # -----------------------------------------------
            # Procurement
            # -----------------------------------------------

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

            # -----------------------------------------------
            # Infrastructure
            # -----------------------------------------------

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
                "quantity",
                1
            ),

            specifications=infrastructure_data.get(
                "specifications",
                ""
            ),

            # -----------------------------------------------
            # Inspection
            # -----------------------------------------------

            physical_condition=inspection_data.get(
                "physicalCondition"
            ),

            accessories_included=inspection_data.get(
                "accessoriesIncluded",
                False
            ),

            passed_inspection=inspection_data.get(
                "passedInspection",
                False
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

        return infrastructure
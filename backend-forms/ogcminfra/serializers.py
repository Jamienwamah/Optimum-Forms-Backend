from rest_framework import serializers
from .models import OGCMInfrastructureReceipt

class OGCMInfrastructureReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = OGCMInfrastructureReceipt
        fields = ['id', 'document_no', 'date_received', 'created_by', 'user_name', 'user_email', 'user_department', 'user_job_title', 'user_company', 'asset_tag', 'po_number', 'invoice_number', 'vendor_supplier', 'delivery_note_number', 'procured_by', 'funding_source', 'category', 'brand_model', 'serial_number', 'quantity', 'specifications', 'physical_condition', 'accessories_included', 'passed_inspection', 'inspected_by', 'inspection_date', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'user_name', 'user_email', 'user_department', 'user_job_title', 'user_company', 'procured_by', 'inspected_by', 'created_at', 'updated_at']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be at least 1.')
        return value
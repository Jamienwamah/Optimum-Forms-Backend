import { Schema, model } from 'mongoose';
import { IInfrastructureReceiptDocument } from '../types/infrastructure-receipt.types';

const ProcurementSchema = new Schema(
  {
    assetTag: { type: String, trim: true },
    poNumber: { type: String, required: true, trim: true, uppercase: true },
    invoiceNumber: { type: String, required: true, trim: true, uppercase: true },
    vendorSupplier: { type: String, required: true, trim: true },
    deliveryNoteNumber: { type: String, required: true, trim: true },
    procuredBy: { type: String, required: true, trim: true },
    fundingSource: { type: String, trim: true },
  },
  { _id: false }
);

const HardwareDetailsSchema = new Schema(
  {
    category: {
      type: String,
      required: true,
      enum: [
        'Server',
        'Desktop Computer',
        'Laptop',
        'Monitor',
        'Printer',
        'Network Switch',
        'Router',
        'Firewall',
        'Wireless Access Point',
        'UPS',
        'NAS/SAN Storage',
        'CCTV Equipment',
        'Biometric',
      ],
    },
    brandModel: { type: String, required: true, trim: true },
    serialNumber: { type: String, required: true, trim: true, uppercase: true },
    quantity: { type: Number, required: true, min: 1, default: 1 },
    specifications: { type: String, trim: true },
  },
  { _id: false }
);

const QualityInspectionSchema = new Schema(
  {
    physicalCondition: {
      type: String,
      required: true,
      enum: ['New / Intact', 'Good Condition', 'Damaged Box', 'Defective'],
      default: 'New / Intact',
    },
    accessoriesIncluded: { type: Boolean, default: true },
    passedInspection: { type: Boolean, required: true, default: true },
    inspectedBy: { type: String, required: true, trim: true },
    inspectionDate: { type: Date, required: true },
    notes: { type: String, trim: true },
  },
  { _id: false }
);

const InfrastructureReceiptSchema = new Schema<IInfrastructureReceiptDocument>(
  {
    documentNo: { type: String, required: true, unique: true, trim: true, uppercase: true },
    dateReceived: { type: Date, required: true, default: Date.now },
    procurement: { type: ProcurementSchema, required: true },
    infrastructure: { type: HardwareDetailsSchema, required: true },
    inspection: { type: QualityInspectionSchema, required: true },
  },
  {
    timestamps: true,
  }
);

// Indexes for query performance
InfrastructureReceiptSchema.index({ documentNo: 1 });
InfrastructureReceiptSchema.index({ 'infrastructure.serialNumber': 1 });
InfrastructureReceiptSchema.index({ 'procurement.poNumber': 1 });
InfrastructureReceiptSchema.index({ 'infrastructure.category': 1 });

export const InfrastructureReceiptModel = model<IInfrastructureReceiptDocument>(
  'InfrastructureReceipt',
  InfrastructureReceiptSchema
);
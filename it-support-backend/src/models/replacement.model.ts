import { Schema, model, Document } from 'mongoose';
import { baseFormFields } from './base-form.schema';
import { IReplacementForm } from '../types/replacement.types';

export interface IReplacementDocument extends IReplacementForm, Document {}

const CurrentDeviceInfoSchema = new Schema(
  {
    assetTag: { type: String, required: true, uppercase: true, trim: true, index: true },
    serialNumber: { type: String, uppercase: true, trim: true },
    currentModel: { type: String, trim: true },
    deviceCondition: {
      type: String,
      required: true,
      enum: ['Non-Functional', 'Intermittent Issues', 'Usable with Defect', 'Missing / Stolen'],
    },
  },
  { _id: false }
);

const ReplacementDetailsSchema = new Schema(
  {
    reason: {
      type: String,
      required: true,
      enum: [
        'Hardware Failure / Beyond Economical Repair',
        'Physical Damage',
        'End of Life (EOL) / Aged Device',
        'Stolen or Lost Device',
        'Role Change / Performance Upgrade Needed',
      ],
    },
    detailedJustification: { type: String, required: true, trim: true },
    requestedDeviceCategory: {
      type: String,
      required: true,
      enum: ['Laptop', 'Desktop Workstation', 'Mobile Device', 'Specialized Hardware'],
    },
    preferredModelOrSpecs: { type: String, trim: true },
    incidentReportNumber: { type: String, trim: true },
    urgency: {
      type: String,
      required: true,
      enum: ['Standard', 'Urgent', 'Critical (Zero Productivity)'],
      default: 'Standard',
    },
  },
  { _id: false }
);

const ReplacementSchema = new Schema<IReplacementDocument>(
  {
    ...baseFormFields,
    currentDevice: { type: CurrentDeviceInfoSchema, required: true },
    replacement: { type: ReplacementDetailsSchema, required: true },
    officialUse: {
      approvedByManager: { type: String, trim: true },
      managerApprovalDate: { type: Date },
      itApprovalStatus: {
        type: String,
        enum: ['Pending Review', 'Approved', 'Rejected', 'On Hold'],
        default: 'Pending Review',
      },
      allocatedNewAssetTag: { type: String, uppercase: true, trim: true },
      allocatedNewSerialNumber: { type: String, uppercase: true, trim: true },
      fulfillmentDate: { type: Date },
      oldDeviceReturned: { type: Boolean, default: false },
      oldDeviceReturnDate: { type: Date },
    },
  },
  {
    timestamps: true,
  }
);

// Indexes for asset lifecycle tracking and pending approvals
ReplacementSchema.index({ 'currentDevice.assetTag': 1 });
ReplacementSchema.index({ 'officialUse.itApprovalStatus': 1, createdAt: -1 });

export const ReplacementModel = model<IReplacementDocument>(
  'DeviceReplacement',
  ReplacementSchema
);
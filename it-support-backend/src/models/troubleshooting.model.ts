import { Schema, model, Document } from 'mongoose';
import { baseFormFields } from './base-form.schema';
import { ITroubleshootingForm } from '../types/troubleshooting.types';

export interface ITroubleshootingDocument extends ITroubleshootingForm, Document {}

const DeviceInfoSchema = new Schema(
  {
    assetTag: { type: String, required: true, uppercase: true, trim: true, index: true },
    serialNumber: { type: String, uppercase: true, trim: true },
    deviceCategory: {
      type: String,
      required: true,
      enum: ['Laptop', 'Desktop', 'Mobile', 'Monitor', 'Peripheral', 'Network Equipment'],
    },
    modelOrMake: { type: String, trim: true },
    operatingSystem: { type: String, trim: true },
  },
  { _id: false }
);

const IssueDetailsSchema = new Schema(
  {
    issueCategory: {
      type: String,
      required: true,
      enum: ['Hardware', 'Software', 'Operating System', 'Network / VPN', 'Peripherals', 'Security / Malware'],
    },
    symptomSummary: { type: String, required: true, trim: true },
    detailedDescription: { type: String, required: true, trim: true },
    errorMessages: { type: String, trim: true },
    stepsAlreadyAttempted: { type: String, trim: true },
    urgency: {
      type: String,
      required: true,
      enum: ['Low', 'Medium', 'High', 'Critical (Work Stopped)'],
      default: 'Medium',
    },
    firstObservedAt: { type: Date, default: Date.now },
  },
  { _id: false }
);

const TroubleshootingSchema = new Schema<ITroubleshootingDocument>(
  {
    ...baseFormFields,
    device: { type: DeviceInfoSchema, required: true },
    issue: { type: IssueDetailsSchema, required: true },
    officialUse: {
      assignedTechnician: { type: String, trim: true },
      technicianEmail: { type: String, trim: true, lowercase: true },
      internalPriority: { type: String, enum: ['P1', 'P2', 'P3', 'P4'], default: 'P3' },
      rootCauseCategory: { type: String, trim: true },
      actionTakenNotes: { type: String, trim: true },
      resolvedAt: { type: Date },
    },
  },
  {
    timestamps: true,
  }
);

// Compound indexing for rapid lookups in large IT operations
TroubleshootingSchema.index({ 'device.assetTag': 1, status: 1 });
TroubleshootingSchema.index({ 'issue.urgency': 1, createdAt: -1 });

export const TroubleshootingModel = model<ITroubleshootingDocument>(
  'DeviceTroubleshooting',
  TroubleshootingSchema
);
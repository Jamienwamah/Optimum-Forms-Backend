import { BaseEmployeeMeta, IBaseForm } from './base-form.types';

export type ReplacementReason =
  | 'Hardware Failure / Beyond Economical Repair'
  | 'Physical Damage'
  | 'End of Life (EOL) / Aged Device'
  | 'Stolen or Lost Device'
  | 'Role Change / Performance Upgrade Needed';

export type DeviceCondition = 'Non-Functional' | 'Intermittent Issues' | 'Usable with Defect' | 'Missing / Stolen';

export interface CurrentDeviceInfo {
  assetTag: string;           // e.g., "LAP-2021-044"
  serialNumber?: string;      // e.g., "8HK92011"
  currentModel?: string;      // e.g., "HP EliteBook 840 G5"
  deviceCondition: DeviceCondition;
}

export interface ReplacementDetails {
  reason: ReplacementReason;
  detailedJustification: string;    // Business reason or incident details
  requestedDeviceCategory: 'Laptop' | 'Desktop Workstation' | 'Mobile Device' | 'Specialized Hardware';
  preferredModelOrSpecs?: string;   // e.g., "MacBook Pro 16\" M3 Max or equivalent 32GB RAM"
  incidentReportNumber?: string;    // Required if stolen/lost (Police or Security ref)
  urgency: 'Standard' | 'Urgent' | 'Critical (Zero Productivity)';
}

export interface ReplacementOfficialUse {
  approvedByManager?: string;
  managerApprovalDate?: Date;
  itApprovalStatus?: 'Pending Review' | 'Approved' | 'Rejected' | 'On Hold';
  allocatedNewAssetTag?: string;     // The new asset tag assigned upon dispatch
  allocatedNewSerialNumber?: string;
  fulfillmentDate?: Date;
  oldDeviceReturned?: boolean;
  oldDeviceReturnDate?: Date;
}

export interface IReplacementForm extends IBaseForm {
  currentDevice: CurrentDeviceInfo;
  replacement: ReplacementDetails;
  officialUse?: ReplacementOfficialUse;
}
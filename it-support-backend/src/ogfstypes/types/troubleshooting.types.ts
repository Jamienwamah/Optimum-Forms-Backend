import { BaseEmployeeMeta, IBaseForm } from './base-form.types';

export type DeviceCategory = 'Laptop' | 'Desktop' | 'Mobile' | 'Monitor' | 'Peripheral' | 'Network Equipment';
export type IssueCategory = 'Hardware' | 'Software' | 'Operating System' | 'Network / VPN' | 'Peripherals' | 'Security / Malware';
export type UrgencyLevel = 'Low' | 'Medium' | 'High' | 'Critical (Work Stopped)';

export interface DeviceInfo {
  assetTag: string;          // e.g., "LAP-2024-009"
  serialNumber?: string;     // e.g., "5CG123456X"
  deviceCategory: DeviceCategory;
  modelOrMake?: string;      // e.g., "Dell Latitude 5530" or "MacBook Pro M2"
  operatingSystem?: string;  // e.g., "Windows 11 Pro" or "macOS Sonoma"
}

export interface IssueDetails {
  issueCategory: IssueCategory;
  symptomSummary: string;           // Short title/summary of problem
  detailedDescription: string;      // Full elaboration
  errorMessages?: string;           // Any visible codes or popups
  stepsAlreadyAttempted?: string;   // e.g., "Rebooted device, reconnected Wi-Fi"
  urgency: UrgencyLevel;
  firstObservedAt?: Date;
}

export interface TroubleshootingOfficialUse {
  assignedTechnician?: string;
  technicianEmail?: string;
  internalPriority?: 'P1' | 'P2' | 'P3' | 'P4';
  rootCauseCategory?: string;       // e.g., "Failed RAM", "Corrupted Registry"
  actionTakenNotes?: string;
  resolvedAt?: Date;
}

export interface ITroubleshootingForm extends IBaseForm {
  device: DeviceInfo;
  issue: IssueDetails;
  officialUse?: TroubleshootingOfficialUse;
}
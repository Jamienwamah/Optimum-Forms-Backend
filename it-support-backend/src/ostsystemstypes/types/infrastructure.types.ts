import { Document } from 'mongoose';

export interface ProcurementDetails {
  assetTag?: string;
  poNumber: string;
  invoiceNumber: string;
  vendorSupplier: string;
  deliveryNoteNumber: string;
  procuredBy: string;
  fundingSource?: string;
}

export interface InfrastructureHardwareDetails {
  category:
    | 'Server'
    | 'Desktop Computer'
    | 'Laptop'
    | 'Monitor'
    | 'Printer'
    | 'Network Switch'
    | 'Router'
    | 'Firewall'
    | 'Wireless Access Point'
    | 'UPS'
    | 'NAS/SAN Storage'
    | 'CCTV Equipment'
    | 'Biometric';
  brandModel: string;
  serialNumber: string;
  quantity: number;
  specifications?: string;
}

export interface QualityInspectionDetails {
  physicalCondition:
    | 'New / Intact'
    | 'Good Condition'
    | 'Damaged Box'
    | 'Defective';
  accessoriesIncluded: boolean;
  passedInspection: boolean;
  inspectedBy: string;
  inspectionDate: Date;
  notes?: string;
}

export interface IInfrastructureReceipt {
  documentNo: string;
  dateReceived: Date;
  procurement: ProcurementDetails;
  infrastructure: InfrastructureHardwareDetails;
  inspection: QualityInspectionDetails;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface IInfrastructureReceiptDocument extends IInfrastructureReceipt, Document {}
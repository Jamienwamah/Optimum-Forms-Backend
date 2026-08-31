import { BaseService } from './base.service';
import { IInfrastructureReceiptDocument } from '../models/infrastructure-receipt.model';
import { InfrastructureReceiptRepository } from '../repositories/infrastructure-receipt.repository';

export class InfrastructureReceiptService extends BaseService<IInfrastructureReceiptDocument> {
  private receiptRepo: InfrastructureReceiptRepository;

  constructor() {
    const repo = new InfrastructureReceiptRepository();
    super(repo);
    this.receiptRepo = repo;
  }

  async registerReceipt(data: Partial<IInfrastructureReceiptDocument>): Promise<IInfrastructureReceiptDocument> {
    const existingDoc = await this.receiptRepo.findByDocumentNo(data.documentNo!);
    if (existingDoc) {
      throw new Error(`Receipt with document number '${data.documentNo}' already exists.`);
    }

    const existingSerial = await this.receiptRepo.findBySerialNumber(data.infrastructure?.serialNumber!);
    if (existingSerial) {
      throw new Error(`Asset with serial number '${data.infrastructure?.serialNumber}' has already been registered.`);
    }

    return await this.receiptRepo.create(data);
  }

  async getBySerial(serialNumber: string): Promise<IInfrastructureReceiptDocument | null> {
    return await this.receiptRepo.findBySerialNumber(serialNumber);
  }

  async getByCategory(category: string): Promise<IInfrastructureReceiptDocument[]> {
    return await this.receiptRepo.findByCategory(category);
  }
}
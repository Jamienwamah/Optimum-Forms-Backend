import { BaseRepository } from './base.repository';
import { IInfrastructureReceiptDocument, InfrastructureReceiptModel } from '../models/infrastructure-receipt.model';

export class InfrastructureReceiptRepository extends BaseRepository<IInfrastructureReceiptDocument> {
  constructor() {
    super(InfrastructureReceiptModel);
  }

  async findByDocumentNo(documentNo: string): Promise<IInfrastructureReceiptDocument | null> {
    return await this.model.findOne({ documentNo: documentNo.toUpperCase() }).exec();
  }

  async findBySerialNumber(serialNumber: string): Promise<IInfrastructureReceiptDocument | null> {
    return await this.model.findOne({ 'infrastructure.serialNumber': serialNumber.toUpperCase() }).exec();
  }

  async findByCategory(category: string): Promise<IInfrastructureReceiptDocument[]> {
    return await this.model
      .find({ 'infrastructure.category': category })
      .sort({ createdAt: -1 })
      .exec();
  }
}
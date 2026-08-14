import { BaseRepository } from './base.repository';
import { IReplacementDocument, ReplacementModel } from '../models/replacement.model';

export class ReplacementRepository extends BaseRepository<IReplacementDocument> {
  constructor() {
    super(ReplacementModel);
  }

  // Find all replacement requests originating from a specific old asset
  async findByCurrentAssetTag(assetTag: string): Promise<IReplacementDocument[]> {
    return await this.model
      .find({ 'currentDevice.assetTag': assetTag.toUpperCase() })
      .sort({ createdAt: -1 })
      .exec();
  }

  // Retrieve requests awaiting IT or Manager sign-off
  async findPendingApprovals(): Promise<IReplacementDocument[]> {
    return await this.model
      .find({ 'officialUse.itApprovalStatus': 'Pending Review' })
      .sort({ createdAt: 1 })
      .exec();
  }
}
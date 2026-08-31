import { BaseRepository } from './base.repository';
import { ITroubleshootingDocument, TroubleshootingModel } from '../models/troubleshooting.model';

export class TroubleshootingRepository extends BaseRepository<ITroubleshootingDocument> {
  constructor() {
    super(TroubleshootingModel);
  }

  // Custom queries specific to troubleshooting tickets
  async findByAssetTag(assetTag: string): Promise<ITroubleshootingDocument[]> {
    return await this.model.find({ 'device.assetTag': assetTag.toUpperCase() }).sort({ createdAt: -1 }).exec();
  }

  async findCriticalOpenTickets(): Promise<ITroubleshootingDocument[]> {
    return await this.model
      .find({
        'issue.urgency': 'Critical (Work Stopped)',
        status: { $ne: 'completed' },
      })
      .sort({ createdAt: 1 })
      .exec();
  }
}
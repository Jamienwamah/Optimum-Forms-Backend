import { BaseService } from './base.service';
import { ITroubleshootingDocument } from '../models/troubleshooting.model';
import { TroubleshootingRepository } from '../repositories/troubleshooting.repository';

export class TroubleshootingService extends BaseService<ITroubleshootingDocument> {
  private troubleshootingRepo: TroubleshootingRepository;

  constructor() {
    const repo = new TroubleshootingRepository();
    super(repo);
    this.troubleshootingRepo = repo;
  }

  async getHistoryByAsset(assetTag: string): Promise<ITroubleshootingDocument[]> {
    return await this.troubleshootingRepo.findByAssetTag(assetTag);
  }

  async getCriticalUnresolved(): Promise<ITroubleshootingDocument[]> {
    return await this.troubleshootingRepo.findCriticalOpenTickets();
  }
}
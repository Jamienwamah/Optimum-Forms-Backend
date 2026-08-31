import { BaseService } from './base.service';
import { IReplacementDocument } from '../models/replacement.model';
import { ReplacementRepository } from '../repositories/replacement.repository';

export class ReplacementService extends BaseService<IReplacementDocument> {
  private replacementRepo: ReplacementRepository;

  constructor() {
    const repo = new ReplacementRepository();
    super(repo);
    this.replacementRepo = repo;
  }

  async getRequestsByAsset(assetTag: string): Promise<IReplacementDocument[]> {
    return await this.replacementRepo.findByCurrentAssetTag(assetTag);
  }

  async getPendingApprovals(): Promise<IReplacementDocument[]> {
    return await this.replacementRepo.findPendingApprovals();
  }
}
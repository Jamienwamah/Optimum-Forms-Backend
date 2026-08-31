import { Request, Response } from 'express';
import { GenericFormController } from './generic-form.controller';
import { IReplacementDocument } from '../models/replacement.model';
import { ReplacementService } from '../services/replacement.service';

class ReplacementControllerClass extends GenericFormController<IReplacementDocument> {
  private rService: ReplacementService;

  constructor(service: ReplacementService) {
    super(service);
    this.rService = service;
  }

  // Endpoint to fetch replacement requests by old asset tag
  getByAssetTag = async (req: Request, res: Response): Promise<void> => {
    try {
      const { assetTag } = req.params;
      const history = await this.rService.getRequestsByAsset(assetTag);
      res.status(200).json({ success: true, count: history.length, data: history });
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  };

  // Endpoint to get all replacements pending IT approval
  getPendingApprovals = async (_req: Request, res: Response): Promise<void> => {
    try {
      const pending = await this.rService.getPendingApprovals();
      res.status(200).json({ success: true, count: pending.length, data: pending });
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  };
}

const serviceInstance = new ReplacementService();
export const ReplacementController = new ReplacementControllerClass(serviceInstance);
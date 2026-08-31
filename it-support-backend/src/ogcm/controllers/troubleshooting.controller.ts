import { Request, Response } from 'express';
import { GenericFormController } from './generic-form.controller';
import { ITroubleshootingDocument } from '../models/troubleshooting.model';
import { TroubleshootingService } from '../services/troubleshooting.service';

class TroubleshootingControllerClass extends GenericFormController<ITroubleshootingDocument> {
  private tService: TroubleshootingService;

  constructor(service: TroubleshootingService) {
    super(service);
    this.tService = service;
  }

  // Custom controller endpoint for asset ticket history
  getByAssetTag = async (req: Request, res: Response): Promise<void> => {
    try {
      const { assetTag } = req.params;
      const history = await this.tService.getHistoryByAsset(assetTag);
      res.status(200).json({ success: true, count: history.length, data: history });
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  };

  // Custom controller endpoint for urgent tickets dashboard view
  getCriticalTickets = async (_req: Request, res: Response): Promise<void> => {
    try {
      const criticals = await this.tService.getCriticalUnresolved();
      res.status(200).json({ success: true, count: criticals.length, data: criticals });
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  };
}

const serviceInstance = new TroubleshootingService();
export const TroubleshootingController = new TroubleshootingControllerClass(serviceInstance);
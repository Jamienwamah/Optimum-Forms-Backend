import { Request, Response } from 'express';
import { GenericFormController } from './generic-form.controller';
import { IInfrastructureReceiptDocument } from '../models/infrastructure-receipt.model';
import { InfrastructureReceiptService } from '../services/infrastructure-receipt.service';

class InfrastructureReceiptControllerClass extends GenericFormController<IInfrastructureReceiptDocument> {
  private receiptService: InfrastructureReceiptService;

  constructor(service: InfrastructureReceiptService) {
    super(service);
    this.receiptService = service;
  }

  // Override creation to use validation and domain logic
  createReceipt = async (req: Request, res: Response): Promise<void> => {
    try {
      const newRecord = await this.receiptService.registerReceipt(req.body);
      res.status(201).json({
        success: true,
        message: 'Infrastructure asset registered and logged successfully!',
        data: newRecord,
      });
    } catch (error: any) {
      res.status(400).json({ success: false, error: error.message });
    }
  };

  getBySerial = async (req: Request, res: Response): Promise<void> => {
    try {
      const { serialNumber } = req.params;
      const record = await this.receiptService.getBySerial(serialNumber);

      if (!record) {
        res.status(404).json({ success: false, error: 'Infrastructure record not found' });
        return;
      }

      res.status(200).json({ success: true, data: record });
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  };

  getByCategory = async (req: Request, res: Response): Promise<void> => {
    try {
      const { category } = req.params;
      const records = await this.receiptService.getByCategory(category);
      res.status(200).json({ success: true, count: records.length, data: records });
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  };
}

const serviceInstance = new InfrastructureReceiptService();
export const InfrastructureReceiptController = new InfrastructureReceiptControllerClass(serviceInstance);
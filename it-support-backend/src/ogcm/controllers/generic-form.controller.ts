import { Request, Response } from 'express';
import { Document } from 'mongoose';
import { BaseService } from '../services/base.service';
import { FormStatus } from '../types/base-form.types';

export class GenericFormController<T extends Document> {
  constructor(private readonly service: BaseService<T>) {}

  submitForm = async (req: Request, res: Response): Promise<void> => {
    try {
      if (!req.body?.employee?.employeeId) {
        res.status(400).json({ success: false, error: 'Employee information is missing' });
        return;
      }
      const result = await this.service.submitForm(req.body);
      res.status(201).json({ success: true, message: 'Submitted successfully', data: result });
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  };

  listForms = async (req: Request, res: Response): Promise<void> => {
    try {
      const { status, employeeId, page, limit } = req.query;
      const results = await this.service.fetchForms({
        status: status as FormStatus,
        employeeId: employeeId as string,
        page: page ? parseInt(page as string, 10) : 1,
        limit: limit ? parseInt(limit as string, 10) : 20,
      });
      res.status(200).json({ success: true, ...results });
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  };

  getFormById = async (req: Request, res: Response): Promise<void> => {
    try {
      const form = await this.service.fetchFormById(req.params.id);
      if (!form) {
        res.status(404).json({ success: false, error: 'Form not found' });
        return;
      }
      res.status(200).json({ success: true, data: form });
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  };

  updateITSection = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params;
      const { officialUse, status } = req.body;
      const updated = await this.service.processITReview(id, officialUse, status);
      if (!updated) {
        res.status(404).json({ success: false, error: 'Form not found' });
        return;
      }
      res.status(200).json({ success: true, message: 'Updated successfully', data: updated });
    } catch (error: any) {
      res.status(500).json({ success: false, error: error.message });
    }
  };
}
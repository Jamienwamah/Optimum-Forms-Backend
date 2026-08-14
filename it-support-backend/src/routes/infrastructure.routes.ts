import { Router } from 'express';
import { InfrastructureReceiptController } from '../controllers/infrastructure-receipt.controller';
import { validateRequest } from '../middlewares/validate-request.middleware';
import { createInfrastructureReceiptSchema } from '../validations/infrastructure-receipt.validation';

const router = Router();

// Registration & Retrieval
router.post(
  '/',
  validateRequest(createInfrastructureReceiptSchema),
  InfrastructureReceiptController.createReceipt
);
router.get('/', InfrastructureReceiptController.listForms);
router.get('/:id', InfrastructureReceiptController.getFormById);

// Specialized queries
router.get('/serial/:serialNumber', InfrastructureReceiptController.getBySerial);
router.get('/category/:category', InfrastructureReceiptController.getByCategory);

export default router;
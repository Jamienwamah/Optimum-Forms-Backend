import { Router } from 'express';
import { TroubleshootingController } from '../controllers/troubleshooting.controller';

const router = Router();

// Base generic endpoints
router.post('/', TroubleshootingController.submitForm);
router.get('/', TroubleshootingController.listForms);
router.get('/:id', TroubleshootingController.getFormById);
router.patch('/:id/official-use', TroubleshootingController.updateITSection);

// Troubleshooting-specific specialized endpoints
router.get('/critical/open', TroubleshootingController.getCriticalTickets);
router.get('/asset/:assetTag', TroubleshootingController.getByAssetTag);

export default router;
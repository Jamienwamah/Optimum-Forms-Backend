import { Router } from 'express';
import { ReplacementController } from '../controllers/replacement.controller';

const router = Router();

// Generic CRUD Endpoints
router.post('/', ReplacementController.submitForm);
router.get('/', ReplacementController.listForms);
router.get('/:id', ReplacementController.getFormById);
router.patch('/:id/official-use', ReplacementController.updateITSection);

// Replacement Specific Specialized Endpoints
router.get('/pending/approvals', ReplacementController.getPendingApprovals);
router.get('/asset/:assetTag', ReplacementController.getByAssetTag);

export default router;
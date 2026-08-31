import { Router } from 'express';
import troubleshootingRoutes from './troubleshooting.routes';
import replacementRoutes from './replacement.routes';
import infrastructureRoutes from './infrastructure.routes';

const router = Router();

router.use('/troubleshooting', troubleshootingRoutes);
router.use('/replacement', replacementRoutes);
router.use('/infrastructure', infrastructureRoutes);

export default router;
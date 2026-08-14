import express from 'express';
import cors from 'cors';
import { connectDB } from './config/db';

// 1. Import all route modules
import infrastructureReceiptRoutes from './routes/infrastructure-receipt.routes';
import troubleshootingRoutes from './routes/troubleshooting.routes';
import replacementRoutes from './routes/replacement.routes';

const app = express();

// Middlewares
app.use(cors());
app.use(express.json());

// 2. Register all API resource endpoints
app.use('/api/infrastructure-receipt', infrastructureReceiptRoutes);
app.use('/api/troubleshooting', troubleshootingRoutes);
app.use('/api/replacement', replacementRoutes);

// Database & Server Startup
connectDB().then(() => {
  app.listen(5000, () => {
    console.log('🚀 Server running on http://localhost:5000');
  });
});
import express, { Application } from 'express';
import cors from 'cors';
import apiRoutes from './routes';

const app: Application = express();

app.use(cors());
app.use(express.json());

// Mount clean endpoints:
// /api/troubleshooting
// /api/replacement
// /api/infrastructure
app.use('/api', apiRoutes);

export default app;
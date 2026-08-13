const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// 1. CORS Configuration (Allow Angular dev server)
const corsOptions = {
  origin: process.env.CLIENT_ORIGIN || 'http://localhost:4200',
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
};
app.use(cors(corsOptions));

// 2. Middleware to parse incoming JSON bodies
app.use(express.json());

// 3. Health check route
app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'OK', timestamp: new Date() });
});

// 4. Sample Ticket Route
app.post('/api/tickets', (req, res) => {
  const { deviceType, issue, userEmail } = req.body;

  if (!deviceType || !issue) {
    return res.status(400).json({ error: 'Device type and issue details are required.' });
  }

  // Simulate database save
  const newTicket = {
    id: `TICK-${Math.floor(1000 + Math.random() * 9000)}`,
    deviceType,
    issue,
    userEmail,
    createdAt: new Date()
  };

  res.status(201).json({ message: 'Ticket created successfully', ticket: newTicket });
});

// 5. Start Server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
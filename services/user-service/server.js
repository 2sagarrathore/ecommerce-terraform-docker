const express = require('express');

const app = express();
const PORT = Number(process.env.PORT) || 3001;
const SERVICE = 'user';

const users = [
  { id: 1, name: 'Aarav Sharma', email: 'aarav@example.com', role: 'customer' },
  { id: 2, name: 'Diya Patel', email: 'diya@example.com', role: 'customer' },
  { id: 3, name: 'Kabir Nair', email: 'kabir@example.com', role: 'admin' }
];

app.use(express.json());

// Root endpoint required by the assignment: a plain sample response.
app.get('/', (req, res) => {
  res.type('text/plain').send('user Service Running');
});

// Health endpoint consumed by the frontend and by the EC2 smoke test.
app.get('/health', (req, res) => {
  res.json({
    service: SERVICE,
    status: 'healthy',
    port: PORT,
    uptimeSeconds: Math.round(process.uptime()),
    timestamp: new Date().toISOString()
  });
});

app.get('/users', (req, res) => {
  res.json({ service: SERVICE, count: users.length, users });
});

app.get('/users/:id', (req, res) => {
  const user = users.find((u) => u.id === Number(req.params.id));
  if (!user) {
    return res.status(404).json({ service: SERVICE, error: 'User not found' });
  }
  res.json({ service: SERVICE, user });
});

app.use((req, res) => {
  res.status(404).json({ service: SERVICE, error: 'Not found', path: req.originalUrl });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`[${SERVICE}] user Service Running on port ${PORT}`);
});

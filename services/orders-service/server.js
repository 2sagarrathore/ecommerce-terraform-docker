const express = require('express');

const app = express();
const PORT = Number(process.env.PORT) || 3003;
const SERVICE = 'orders';

const orders = [
  { id: 9001, userId: 1, items: [{ productId: 101, qty: 1 }], total: 899, status: 'DELIVERED' },
  { id: 9002, userId: 2, items: [{ productId: 103, qty: 1 }, { productId: 104, qty: 2 }], total: 28597, status: 'SHIPPED' },
  { id: 9003, userId: 1, items: [{ productId: 102, qty: 1 }], total: 3499, status: 'PENDING' }
];

app.use(express.json());

app.get('/', (req, res) => {
  res.type('text/plain').send('orders Service Running');
});

app.get('/health', (req, res) => {
  res.json({
    service: SERVICE,
    status: 'healthy',
    port: PORT,
    uptimeSeconds: Math.round(process.uptime()),
    timestamp: new Date().toISOString()
  });
});

app.get('/orders', (req, res) => {
  res.json({ service: SERVICE, count: orders.length, orders });
});

app.get('/orders/:id', (req, res) => {
  const order = orders.find((o) => o.id === Number(req.params.id));
  if (!order) {
    return res.status(404).json({ service: SERVICE, error: 'Order not found' });
  }
  res.json({ service: SERVICE, order });
});

app.use((req, res) => {
  res.status(404).json({ service: SERVICE, error: 'Not found', path: req.originalUrl });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`[${SERVICE}] orders Service Running on port ${PORT}`);
});

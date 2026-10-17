const express = require('express');

const app = express();
const PORT = Number(process.env.PORT) || 3004;
const SERVICE = 'cart';

const carts = {
  1: { userId: 1, items: [{ productId: 104, qty: 1, price: 1799 }], total: 1799 },
  2: { userId: 2, items: [{ productId: 101, qty: 2, price: 899 }], total: 1798 }
};

app.use(express.json());

app.get('/', (req, res) => {
  res.type('text/plain').send('cart Service Running');
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

app.get('/cart', (req, res) => {
  const all = Object.values(carts);
  res.json({ service: SERVICE, count: all.length, carts: all });
});

app.get('/cart/:userId', (req, res) => {
  const cart = carts[req.params.userId];
  if (!cart) {
    return res.status(404).json({ service: SERVICE, error: 'Cart not found' });
  }
  res.json({ service: SERVICE, cart });
});

app.use((req, res) => {
  res.status(404).json({ service: SERVICE, error: 'Not found', path: req.originalUrl });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`[${SERVICE}] cart Service Running on port ${PORT}`);
});

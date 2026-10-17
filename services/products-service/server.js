const express = require('express');

const app = express();
const PORT = Number(process.env.PORT) || 3002;
const SERVICE = 'products';

const products = [
  { id: 101, name: 'Wireless Mouse', price: 899, currency: 'INR', stock: 42 },
  { id: 102, name: 'Mechanical Keyboard', price: 3499, currency: 'INR', stock: 17 },
  { id: 103, name: '27" 4K Monitor', price: 24999, currency: 'INR', stock: 8 },
  { id: 104, name: 'USB-C Hub', price: 1799, currency: 'INR', stock: 63 }
];

app.use(express.json());

app.get('/', (req, res) => {
  res.type('text/plain').send('products Service Running');
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

app.get('/products', (req, res) => {
  res.json({ service: SERVICE, count: products.length, products });
});

app.get('/products/:id', (req, res) => {
  const product = products.find((p) => p.id === Number(req.params.id));
  if (!product) {
    return res.status(404).json({ service: SERVICE, error: 'Product not found' });
  }
  res.json({ service: SERVICE, product });
});

app.use((req, res) => {
  res.status(404).json({ service: SERVICE, error: 'Not found', path: req.originalUrl });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`[${SERVICE}] products Service Running on port ${PORT}`);
});

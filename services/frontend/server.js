const express = require('express');
const path = require('path');

const app = express();
const PORT = Number(process.env.PORT) || 3000;
const SERVICE = 'frontend';

// Backend locations are injected as environment variables so the same image
// works with Docker Compose locally and with the EC2 user-data deployment.
const BACKENDS = [
  { key: 'user', label: 'User Service', port: 3001, url: process.env.USER_SERVICE_URL || 'http://user-service:3001' },
  { key: 'products', label: 'Products Service', port: 3002, url: process.env.PRODUCTS_SERVICE_URL || 'http://products-service:3002' },
  { key: 'orders', label: 'Orders Service', port: 3003, url: process.env.ORDERS_SERVICE_URL || 'http://orders-service:3003' },
  { key: 'cart', label: 'Cart Service', port: 3004, url: process.env.CART_SERVICE_URL || 'http://cart-service:3004' }
];

async function probe(backend) {
  const started = Date.now();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 2500);
  try {
    const response = await fetch(`${backend.url}/health`, { signal: controller.signal });
    const body = await response.json();
    return {
      key: backend.key,
      label: backend.label,
      port: backend.port,
      url: backend.url,
      status: response.ok ? 'up' : 'down',
      latencyMs: Date.now() - started,
      detail: body
    };
  } catch (error) {
    return {
      key: backend.key,
      label: backend.label,
      port: backend.port,
      url: backend.url,
      status: 'down',
      latencyMs: Date.now() - started,
      detail: { error: error.name === 'AbortError' ? 'timeout' : error.message }
    };
  } finally {
    clearTimeout(timer);
  }
}

app.use(express.static(path.join(__dirname, 'public')));

app.get('/health', (req, res) => {
  res.json({
    service: SERVICE,
    status: 'healthy',
    port: PORT,
    uptimeSeconds: Math.round(process.uptime()),
    timestamp: new Date().toISOString()
  });
});

// Aggregated status of all four backends, rendered by the homepage.
app.get('/api/status', async (req, res) => {
  const services = await Promise.all(BACKENDS.map(probe));
  res.json({
    frontend: { status: 'up', port: PORT, message: 'Frontend is Live' },
    services,
    healthy: services.filter((s) => s.status === 'up').length,
    total: services.length,
    timestamp: new Date().toISOString()
  });
});

// Proxy to each backend so the demo endpoints are reachable from the browser
// without opening the backend ports to the internet.
const PROXY_PATHS = {
  user: '/users',
  products: '/products',
  orders: '/orders',
  cart: '/cart'
};

app.get('/api/:service', async (req, res) => {
  const backend = BACKENDS.find((b) => b.key === req.params.service);
  if (!backend) {
    return res.status(404).json({ error: 'Unknown service', service: req.params.service });
  }
  try {
    const response = await fetch(`${backend.url}${PROXY_PATHS[backend.key]}`);
    res.status(response.status).json(await response.json());
  } catch (error) {
    res.status(502).json({ error: 'Backend unreachable', service: backend.key, detail: error.message });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`[${SERVICE}] Frontend is Live on port ${PORT}`);
});

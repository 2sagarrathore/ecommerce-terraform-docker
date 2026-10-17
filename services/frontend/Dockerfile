# ---- frontend ------------------------------------------------------------
# Serves the public homepage ("Frontend is Live") and aggregates the health of
# the four backend services over the private Docker network.
FROM node:20-alpine

ENV NODE_ENV=production \
    PORT=3000

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

COPY server.js ./
COPY public ./public

USER node

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O - http://127.0.0.1:3000/health > /dev/null 2>&1 || exit 1

CMD ["node", "server.js"]

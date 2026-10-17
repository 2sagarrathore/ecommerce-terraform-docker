# ---- user-service ----------------------------------------------------------------
# Small, production-only image: deps installed from the lockfile, app runs as
# the unprivileged "node" user that the base image already provides.
FROM node:20-alpine

ENV NODE_ENV=production \
    PORT=3001

WORKDIR /app

# Copy manifests first so the dependency layer is cached across code changes.
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

COPY server.js ./

USER node

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O - http://127.0.0.1:3001/health > /dev/null 2>&1 || exit 1

CMD ["node", "server.js"]

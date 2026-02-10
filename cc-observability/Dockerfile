# Stage 1: Build Vue client
FROM oven/bun:1 AS client-build
WORKDIR /build/client
COPY client/package.json client/bun.lockb* ./
RUN bun install --frozen-lockfile 2>/dev/null || bun install
COPY client/ ./
RUN bun run build

# Stage 2: Install server dependencies
FROM oven/bun:1 AS server-deps
WORKDIR /build/server
COPY server/package.json server/bun.lockb* ./
RUN bun install --production

# Stage 3: Production image
FROM oven/bun:1-slim
WORKDIR /app

# Create data directory for SQLite
RUN mkdir -p /app/data

# Copy server
COPY server/ /app/server/
COPY --from=server-deps /build/server/node_modules /app/server/node_modules

# Copy built client
COPY --from=client-build /build/client/dist /app/client

EXPOSE 4000

ENV NODE_ENV=production
ENV PORT=4000
ENV DB_PATH=/app/data/ccobs.db

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD bun -e "fetch('http://localhost:4000/health').then(r => r.ok ? process.exit(0) : process.exit(1)).catch(() => process.exit(1))"

CMD ["bun", "run", "/app/server/index.ts"]

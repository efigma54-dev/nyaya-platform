FROM node:20.12-bookworm-slim AS deps
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund || npm install --no-audit --no-fund

FROM node:20.12-bookworm-slim AS builder
ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=development
WORKDIR /app
COPY frontend/ ./
COPY --from=deps /app/node_modules ./node_modules
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8000/api/v1}
ENV NEXT_PUBLIC_APP_ENV=${NEXT_PUBLIC_APP_ENV:-development}

EXPOSE 3000
CMD ["sh", "-c", "npm install --no-audit --no-fund 2>/dev/null ; npm run dev -- -p 3000 -H 0.0.0.0"]

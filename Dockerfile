### STAGE 1: Build Frontend (React + Vite)
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
COPY frontend/vite.config.js ./
COPY frontend/postcss.config.* ./
COPY frontend/tailwind.config.js ./
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/index.html ./
RUN npm install
RUN npm run build

### STAGE 2: Build Backend (FastAPI)
FROM python:3.11-slim AS backend-builder
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY main.py ./
COPY dados_exemplo.csv ./
COPY database ./database

### STAGE 3: Production Image
FROM python:3.11-slim
WORKDIR /app
# Copy backend and dependencies
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /app /app
# Copy built frontend
COPY --from=frontend-builder /app/dist ./static
# Create app user
RUN adduser --system --group appuser
RUN mkdir -p /app/logs /app/uploads && chown -R appuser:appuser /app
USER appuser
EXPOSE 8080
# Healthcheck (crie endpoint /api/health no FastAPI)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1
# Start FastAPI with Uvicorn (log detalhado e reload para debug)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "debug", "--reload", "--use-colors"]

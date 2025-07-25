# 🚀 Dockerfile Simplificado para Easypanel
# Dashboard# Copy backend application
COPY backend ./backend
COPY main.py ./
COPY dados_exemplo.csv ./
COPY database ./database

# Copy scripts and set permissions
COPY deploy_easypanel.sh ./
COPY build.sh ./

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/dist ./static

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/uploads /app/temp \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app \
    && chmod +x /app/deploy_easypanel.sh \
    && chmod +x /app/build.shecessary directories and set permissions
RUN mkdir -p /app/logs /app/uploads /app/temp \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app

# Switch to non-root user
USER appuser Urbana - Frontend + Backend

# ==============================================================================
# STAGE 1: Build Frontend (React + Vite)
# ==============================================================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
COPY vite.config.js ./
COPY postcss.config.js ./
COPY tailwind.config.js ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY src ./src
COPY public ./public
COPY index.html ./

# Build for production
RUN npm run build

# ==============================================================================
# STAGE 2: Production Image (Python Flask + Static Files)
# ==============================================================================
FROM python:3.11-slim AS production

WORKDIR /app

# Create non-root user with proper permissions
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies
RUN apt-get update && apt-get install -y 
    gcc 
    libpq-dev 
    curl 
    && rm -rf /var/lib/apt/lists/* 
    && apt-get clean

# Copy requirements and install Python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend ./backend
COPY main.py ./
COPY dados_exemplo.csv ./
COPY database ./database

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/dist ./static

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/uploads /app/temp 
    && chown -R appuser:appuser /app 
    && chmod -R 755 /app 
    && chmod +x /app/main.py

# Switch to non-root user
USER appuser

# Environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 
    CMD curl -f http://localhost:8080/api/health || exit 1

# Start application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "60", "--keep-alive", "2", "--max-requests", "1000", "--max-requests-jitter", "100", "--preload", "main:app"]# ==============================================================================
# STAGE 3: Production Image - Simplified for Easypanel
# ==============================================================================
FROM python:3.11-slim AS production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy Python dependencies from backend-setup stage
COPY --from=backend-setup /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-setup /usr/local/bin /usr/local/bin

# Copy backend application
COPY --from=backend-setup /app ./

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist ./static

# Create app user for security (non-root)
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/uploads \
    && chown -R appuser:appgroup /app \
    && chmod -R 755 /app

# Environment variables for production
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PORT=8080
ENV USER=appuser

# Switch to app user
USER appuser

# Expose port (Easypanel default)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Start gunicorn directly (simpler for Easypanel)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "60", "--keep-alive", "2", "--max-requests", "1000", "--max-requests-jitter", "100", "main:app"]

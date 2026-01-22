# ==========================================
# DOCUMENT MANAGEMENT SYSTEM - DOCKERFILE
# ==========================================
# Multi-stage build for optimized production image

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 dms && \
    chown -R dms:dms /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/dms/.local

# Copy application code
COPY --chown=dms:dms . .

# Create necessary directories and log files with proper permissions
RUN mkdir -p data/db data/exports data/templates logs && \
    touch logs/access.log logs/error.log && \
    chown -R dms:dms data logs && \
    chmod -R 755 data logs

# Switch to non-root user
USER dms

# Set environment variables
ENV PATH=/home/dms/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=src/web_app.py \
    FLASK_ENV=production

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run application with gunicorn (logging to stdout/stderr for Docker)
CMD ["python", "-m", "gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--threads", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "src.web_app:app"]

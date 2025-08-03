# Multi-stage build for Solana NFT Downloader
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy source code
COPY src/ ./src/
COPY main.py .

# Create necessary directories
RUN mkdir -p /app/output /app/logs /app/credentials

# Set environment variables
ENV PYTHONPATH=/app
ENV OUTPUT_DIR=/app/output
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user for security
RUN groupadd -r nftuser && useradd -r -g nftuser nftuser
RUN chown -R nftuser:nftuser /app
RUN chown -R nftuser:nftuser /app/output /app/logs /app/credentials
RUN mkdir -p /home/nftuser/.config/gcloud
RUN chown -R nftuser:nftuser /home/nftuser/.config
USER nftuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
ENTRYPOINT ["python", "main.py"]
CMD ["--help"] 
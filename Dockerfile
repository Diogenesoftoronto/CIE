# Multi-stage Dockerfile for CIE (Optimization & Evaluation)

# Build stage
FROM python:3.13-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /build

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -e . && \
    pip install build

# Copy source code
COPY cie/ ./cie/
COPY README.md ./
COPY LICENSE ./

# Build the package
RUN python -m build

# Runtime stage
FROM python:3.13-slim as runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash cie

# Set work directory
WORKDIR /app

# Copy built package from builder stage
COPY --from=builder /build/dist/*.whl ./

# Install the package
RUN pip install --no-cache-dir *.whl && \
    rm *.whl

# Copy examples and documentation
COPY --from=builder /build/examples ./examples
COPY --from=builder /build/README.md ./

# Create directories for CIE data
RUN mkdir -p /home/cie/.cie/{experiments,config} && \
    chown -R cie:cie /home/cie/.cie

# Switch to non-root user
USER cie

# Set environment variables
ENV PYTHONPATH=/app
ENV CIE_CONFIG_DIR=/home/cie/.cie
ENV CIE_EXPERIMENTS_DIR=/home/cie/.cie/experiments

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD cie --help > /dev/null || exit 1

# Default command
CMD ["cie", "--help"]

# Development stage
FROM runtime as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-asyncio \
    black \
    ruff \
    mypy \
    bandit \
    safety \
    pdoc3

# Copy source code for development
COPY --from=builder /build/cie ./cie
COPY --from=builder /build/tests ./tests
COPY --from=builder /build/pyproject.toml ./

# Install in development mode
RUN pip install -e .

# Switch back to cie user
USER cie

# Development command
CMD ["bash"]

# Production stage with minimal footprint
FROM runtime as production

# Labels for metadata
LABEL maintainer="CIE Team <cie@example.com>"
LABEL version="0.2.0"
LABEL description="CIE (Optimization & Evaluation) - AI-powered optimization framework"
LABEL org.opencontainers.image.source="https://github.com/cie-team/cie"
LABEL org.opencontainers.image.documentation="https://cie.readthedocs.io"
LABEL org.opencontainers.image.licenses="MIT"

# Expose port for potential web interface (future)
EXPOSE 8080

# Production command
CMD ["cie", "tui"]
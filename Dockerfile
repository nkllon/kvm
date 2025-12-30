# Dockerfile for NKLLON Hardware Topology System
FROM python:3.11-slim

LABEL maintainer="NKLLON"
LABEL description="Hardware topology validation system using RDF/OWL and SHACL"

WORKDIR /app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock* ./
COPY src/ ./src/
COPY ontology/ ./ontology/
COPY data/ ./data/

# Install dependencies
RUN uv pip install --system -e ".[dev]"

# Create output directory for reports
RUN mkdir -p /app/reports

# Set environment variable
ENV NKLLON_PROJECT_ROOT=/app

# Default command: run validation
CMD ["uv", "run", "python", "-m", "nkllon.validate"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD uv run python -c "from nkllon.config import default_config; print('healthy')" || exit 1

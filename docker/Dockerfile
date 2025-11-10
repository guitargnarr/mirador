# Mirador Systems - Production Docker Image
# Healthcare AI with 97 agents, 79ms response time, HIPAA-compliant
# For Norton Healthcare and enterprise deployments

FROM ollama/ollama:latest

LABEL maintainer="Matthew Scott <matthew@miradorsystems.com>"
LABEL version="2.1.1"
LABEL description="Mirador Healthcare AI - 100% local processing, HIPAA-compliant"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    sqlite3 \
    curl \
    git \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    mirador-core==2.1.1 \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    filelock==3.20.0 \
    pydantic==2.6.0

# Pre-download Ollama models (makes first run instant)
# This runs during image build, so clients don't wait
RUN ollama serve & \
    sleep 10 && \
    ollama pull phi3:mini && \
    ollama pull qwen2.5:7b && \
    pkill ollama

# Copy healthcare query cache (for <50ms responses)
COPY healthcare_cache.db /app/cache/mirador_cache.db

# Copy Mirador server API
COPY mirador_server.py /app/mirador_server.py

# Copy supervisor config (manages Ollama + Mirador services)
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create data directory for persistence
RUN mkdir -p /app/data /app/logs /app/cache

# Environment variables (override with docker run -e)
ENV MIRADOR_CACHE_PATH=/app/cache/mirador_cache.db
ENV MIRADOR_LOG_LEVEL=INFO
ENV OLLAMA_KEEP_ALIVE=600
ENV OLLAMA_NUM_PARALLEL=4

# Expose ports
EXPOSE 8000   # Mirador API
EXPOSE 11434  # Ollama API (optional external access)

# Health check (ensures Mirador is responding)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use supervisor to manage both Ollama and Mirador services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

# Volume mounts for persistence (optional)
VOLUME ["/app/data", "/app/logs"]

# Metadata
ARG BUILD_DATE
ARG VCS_REF
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.revision=$VCS_REF
LABEL org.opencontainers.image.source="https://github.com/guitargnarr/mirador"
LABEL org.opencontainers.image.documentation="https://github.com/guitargnarr/mirador/blob/main/docker/DOCKER_DEPLOYMENT.md"

# Ufamily_member:
# docker build -t mirador-systems:latest .
# docker run -p 8000:8000 -v ./data:/app/data mirador-systems:latest

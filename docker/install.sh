#!/bin/bash
# Mirador Systems - One-Command Installation
# For Norton Healthcare and enterprise deployments

set -e  # Exit on error

echo "========================================"
echo "MIRADOR SYSTEMS - INSTALLATION"
echo "Healthcare AI Deployment"
echo "========================================"
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo "⚠️  Please do not run as root"
   echo "   Run as regular user with Docker permissions"
   exit 1
fi

# Check Docker installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    echo "   Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✓ Docker found: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose not found, using 'docker compose' instead"
    COMPOSE_CMD="docker compose"
else
    echo "✓ Docker Compose found: $(docker-compose --version)"
    COMPOSE_CMD="docker-compose"
fi

# Check Docker daemon running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon not running"
    echo "   Start Docker Desktop or run: sudo systemctl start docker"
    exit 1
fi

echo "✓ Docker daemon running"
echo

# Pull or build image
echo "========================================"
echo "BUILDING MIRADOR IMAGE"
echo "========================================"
echo

if [ -f "Dockerfile" ]; then
    echo "Building Mirador image from local Dockerfile..."
    docker build -t mirador-systems:latest \
      --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
      --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "local") \
      .

    if [ $? -eq 0 ]; then
        echo "✓ Image built successfully"
    else
        echo "❌ Image build failed"
        exit 1
    fi
else
    echo "Pulling pre-built image from Docker Hub..."
    docker pull guitargnarr/mirador-systems:latest
    docker tag guitargnarr/mirador-systems:latest mirador-systems:latest
fi

echo

# Create data directories
echo "========================================"
echo "SETTING UP DATA DIRECTORIES"
echo "========================================"
echo

mkdir -p ./data ./logs ./cache
echo "✓ Created data directories"

# Copy .env.example if .env doesn't exist
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "✓ Created .env from .env.example"
    echo "   Edit .env to customize configuration"
fi

echo

# Start services
echo "========================================"
echo "STARTING MIRADOR SERVICES"
echo "========================================"
echo

if [ -f "docker-compose.yml" ]; then
    $COMPOSE_CMD up -d
else
    # Fallback to docker run if no compose file
    docker run -d \
      --name mirador-healthcare-ai \
      -p 8000:8000 \
      -p 11434:11434 \
      -v $(pwd)/data:/app/data \
      -v $(pwd)/logs:/app/logs \
      -v $(pwd)/cache:/app/cache \
      --restart unless-stopped \
      mirador-systems:latest
fi

echo "✓ Mirador started"
echo

# Wait for health check
echo "========================================"
echo "HEALTH CHECK"
echo "========================================"
echo

echo "Waiting for Mirador to be ready..."
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Mirador is healthy!"
        break
    fi

    if [ $i -eq 30 ]; then
        echo "❌ Health check timeout"
        echo "   Check logs: docker logs mirador-healthcare-ai"
        exit 1
    fi

    echo -n "."
    sleep 2
done

echo
echo

# Success summary
echo "========================================"
echo "✅ INSTALLATION COMPLETE"
echo "========================================"
echo

echo "Mirador Healthcare AI is now running!"
echo

echo "📊 Access Points:"
echo "  API: http://localhost:8000"
echo "  Health Check: http://localhost:8000/health"
echo "  Stats: http://localhost:8000/stats"
echo "  Documentation: http://localhost:8000/docs"
echo

echo "🧪 Test Query:"
echo "  curl -X POST http://localhost:8000/query \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"query\": \"What is the copay for a specialist visit?\"}'"
echo

echo "📝 Logs:"
echo "  docker logs mirador-healthcare-ai"
echo "  docker logs -f mirador-healthcare-ai  # Follow mode"
echo

echo "🛑 Stop Services:"
if [ -f "docker-compose.yml" ]; then
    echo "  $COMPOSE_CMD down"
else
    echo "  docker stop mirador-healthcare-ai"
fi

echo
echo "🎉 Ready for Norton Healthcare pilot!"
echo "========================================"

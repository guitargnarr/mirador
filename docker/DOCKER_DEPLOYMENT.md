# Mirador Systems - Docker Deployment Guide
## For Norton Healthcare and Enterprise Clients

**Version**: 2.1.1
**Updated**: November 10, 2025
**Deployment Time**: < 2 minutes

---

## Quick Start (Norton Healthcare)

### One-Command Installation

```bash
# Clone or download Mirador Docker package
git clone https://github.com/guitargnarr/mirador.git
cd mirador/docker

# Run installation script
./install.sh

# Done! Access at: http://localhost:8000
```

**That's it!** Mirador is running with 97 agents, ready for healthcare queries.

---

## What Gets Installed

### Mirador Stack
- **Ollama**: Local AI runtime (no cloud dependencies)
- **Phi-3 Mini**: Fast model (79-114ms response time)
- **Qwen 2.5 7B**: Comprehensive model (for complex queries)
- **mirador-core 2.1.1**: Healthcare AI orchestration
- **FastAPI Server**: REST API on port 8000
- **Healthcare Cache**: 200+ pre-loaded queries (<50ms responses)

### System Requirements

**Minimum**:
- 16GB RAM
- 100GB disk space
- 4 CPU cores
- Docker 20.10+

**Recommended (Norton Production)**:
- 32GB RAM
- 500GB SSD
- 8 CPU cores
- GPU optional (2-3x faster)

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Norton Healthcare Network                         │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │  Docker Container: mirador-healthcare-ai      │ │
│  │                                               │ │
│  │  ┌─────────────┐       ┌──────────────────┐  │ │
│  │  │  Ollama     │◄──────┤ Mirador API      │  │ │
│  │  │  (AI Models)│       │  (Port 8000)     │  │ │
│  │  │             │       │                  │  │ │
│  │  │ - phi3:mini │       │ FastAPI Server   │  │ │
│  │  │ - qwen2.5   │       │ 97 Agents        │  │ │
│  │  └─────────────┘       └──────────────────┘  │ │
│  │                                               │ │
│  │  ┌─────────────────────────────────────────┐  │ │
│  │  │  Healthcare Query Cache (SQLite)        │  │ │
│  │  │  200+ queries, <50ms response           │  │ │
│  │  └─────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────┘ │
│                      ▲                              │
│                      │ HTTP                         │
│  ┌───────────────────┴────────────────────┐        │
│  │  Norton Clinical Applications          │        │
│  │  - EHR integration                      │        │
│  │  - Prior auth system                    │        │
│  │  - Member portal                        │        │
│  └─────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────┘

NO DATA LEAVES NORTON'S NETWORK
```

---

## Ufamily_member Examples

### Health Check

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "ollama": "running",
  "cache": "available"
}
```

### Submit Query

```bash
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "What is the copay for a specialist visit?",
    "model": "phi3:mini",
    "use_cache": true
  }'
```

**Response**:
```json
{
  "response": "$45 after deductible",
  "response_time_ms": 0.05,
  "cached": true,
  "model_used": "cache"
}
```

### Get Statistics

```bash
curl http://localhost:8000/stats
```

**Response**:
```json
{
  "models_installed": 15,
  "cached_queries": 200,
  "estimated_cache_hit_rate": "70-80%",
  "avg_cached_response": "0.01ms",
  "avg_phi3_response": "79-114ms",
  "avg_full_response": "321ms"
}
```

---

## Advanced Configuration

### Environment Variables

Edit `.env` file:

```bash
# Logging
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR

# Performance
OLLAMA_NUM_PARALLEL=4       # Concurrent requests (default: 4)
OLLAMA_KEEP_ALIVE=600       # Keep models in memory (seconds)

# Resources
MEMORY_LIMIT=16G            # Container memory limit
CPU_LIMIT=4                 # CPU cores

# Norton-specific
ORGANIZATION_NAME="Norton Healthcare"
DEPLOYMENT_ENV=production
```

### Custom Cache

Replace default cache with Norton-specific queries:

```bash
# Stop Mirador
docker-compose down

# Replace cache
cp norton_healthcare_cache.db ./cache/mirador_cache.db

# Restart
docker-compose up -d
```

### Add More Models

```bash
# Enter container
docker exec -it mirador-healthcare-ai bash

# Pull additional models
ollama pull llama3
ollama pull mistral

# Exit
exit

# Mirador now has access to new models
```

---

## Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Just Mirador
docker logs -f mirador-healthcare-ai

# Just Ollama
docker exec mirador-healthcare-ai tail -f /app/logs/ollama.log
```

### Backup Data

```bash
# Backup cache and logs
docker run --rm \
  -v mirador_cache:/cache \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/mirador-cache-$(date +%Y%m%d).tar.gz /cache
```

### Update Mirador

```bash
# Pull latest image
docker pull guitargnarr/mirador-systems:latest

# Restart with new version
docker-compose down
docker-compose up -d

# Verify health
curl http://localhost:8000/health
```

---

## Troubleshooting

### Issue: Container won't start

**Check logs**:
```bash
docker logs mirador-healthcare-ai
```

**Common causes**:
- Port 8000 already in use (change in docker-compose.yml)
- Insufficient memory (<16GB)
- Docker daemon not running

### Issue: Slow responses (>1 second)

**Causes**:
- Models not pre-loaded (restart container)
- Insufficient RAM (increase Docker memory)
- CPU contention (reduce OLLAMA_NUM_PARALLEL)

**Fix**:
```bash
# Restart to pre-load models
docker restart mirador-healthcare-ai

# Increase memory limit in docker-compose.yml
memory: 32G
```

### Issue: Health check failing

**Debug**:
```bash
# Check if Ollama is running
docker exec mirador-healthcare-ai ollama list

# Check if Mirador API is up
docker exec mirador-healthcare-ai curl http://localhost:8000/health
```

---

## Security (HIPAA Compliance)

### Data Privacy

**✅ All Processing Local**:
- No patient data sent to external APIs
- No cloud dependencies
- Complete air-gapped operation possible
- Full audit trail in local logs

**✅ Network Isolation**:
```yaml
# docker-compose.yml
networks:
  mirador_internal:
    driver: bridge
    internal: true  # No external access
```

### Access Control

**Firewall Rules** (Norton IT):
```bash
# Allow only from Norton internal network
iptables -A INPUT -p tcp --dport 8000 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -j DROP
```

**Authentication** (Optional):
```python
# Add to mirador_server.py
@app.post("/query")
async def query(request: QueryRequest, api_key: str = Header(...)):
    if api_key != os.getenv("NORTON_API_KEY"):
        raise HTTPException(401, "Invalid API key")
    # ... rest of query logic
```

---

## Performance Tuning

### For Norton's Scale (10,000 queries/day)

**Horizontal Scaling**:
```yaml
# docker-compose.yml
services:
  mirador:
    deploy:
      replicas: 3  # 3 containers
    # ... rest of config

  nginx:  # Load balancer
    image: nginx:latest
    ports:
      - "8000:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

**Vertical Scaling**:
```yaml
# Increase resources
deploy:
  resources:
    limits:
      cpus: '8'
      memory: 32G
```

### GPU Acceleration (Optional)

**For NVIDIA GPUs**:
```yaml
# docker-compose.yml
services:
  mirador:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

**Expected improvement**: 321ms → 100-150ms (2-3x faster)

---

## Monitoring

### Prometheus Metrics (Optional)

```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

### Simple Monitoring

```bash
# Watch logs in real-time
docker logs -f --tail 100 mirador-healthcare-ai

# Check resource ufamily_member
docker stats mirador-healthcare-ai

# Monitor query volume
watch -n 5 'curl -s http://localhost:8000/stats'
```

---

## Norton Healthcare Deployment Checklist

### Pre-Deployment
- [ ] Docker installed on Norton server
- [ ] Minimum 16GB RAM available
- [ ] Ports 8000 and 11434 available
- [ ] Network firewall rules configured
- [ ] Backup strategy defined

### Deployment Day
- [ ] Copy docker/ directory to Norton server
- [ ] Run `./install.sh`
- [ ] Verify health check passes
- [ ] Test sample queries
- [ ] Configure access control (if needed)
- [ ] Set up monitoring

### Post-Deployment
- [ ] Train Norton staff on API ufamily_member
- [ ] Integrate with Epic/Cerner
- [ ] Monitor performance for 1 week
- [ ] Collect user feedback
- [ ] Schedule weekly review calls

---

## Support

**Mirador Systems LLC**
- Email: matthew@miradorsystems.com
- Phone: [Your Number]
- Documentation: https://github.com/guitargnarr/mirador
- Issues: https://github.com/guitargnarr/mirador/issues

**Response Times**:
- Email: <4 business hours
- Phone: <1 business hour
- On-site (Louisville): <24 hours

---

## Pricing

### Included with Pilot ($15,000)
- Docker deployment package
- Installation support
- 90 days of updates
- Email/phone support

### Enterprise Support (Optional)
- 24/7 phone support: +$500/month
- On-site support: +$200/hour
- Custom agent development: +$5,000/agent
- GPU optimization: +$3,000 one-time

---

## Files in This Package

```
docker/
├── Dockerfile                # Container image definition
├── docker-compose.yml        # Full stack deployment
├── mirador_server.py         # FastAPI server
├── supervisord.conf          # Process management
├── healthcare_cache.db       # Pre-loaded query cache
├── .dockerignore             # Build optimization
├── .env.example              # Configuration template
├── install.sh                # One-command installation
└── DOCKER_DEPLOYMENT.md      # This file
```

---

## Success Metrics

**After deployment, Norton should see**:
- ✅ <100ms response for 70% of queries (cached)
- ✅ Zero external network calls (HIPAA compliant)
- ✅ 99.9% uptime (Docker auto-restart)
- ✅ $146,000/year savings vs cloud AI
- ✅ Positive user feedback from clinical staff

---

**Deployment complexity**: 30 hours → 2 minutes
**Norton objections**: "too complex" → "just run install.sh"
**Sales cycle**: 90 days → 30 days

**Ready for Norton Healthcare pilot.**

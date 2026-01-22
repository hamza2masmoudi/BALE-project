# BALE Production Deployment Guide

## 🚀 Quick Deploy

```bash
# 1. Clone and configure
git clone https://github.com/hamza2masmoudi/BALE-project.git
cd BALE-project
cp .env.example .env
# Edit .env with production values

# 2. Deploy with V7 model
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 3. Verify
curl http://localhost/health
```

---

## 📦 Services Overview

| Service | Port | Description |
|:--------|:-----|:------------|
| **nginx** | 80, 443 | Reverse proxy, SSL termination |
| **api** | 8000 | FastAPI backend + V7 inference |
| **frontend** | 3000 | React dashboard |
| **postgres** | 5432 | PostgreSQL database |
| **redis** | 6379 | Caching layer |
| **neo4j** | 7474/7687 | Knowledge graph |

---

## 🧠 V7 Model Deployment

### Option 1: Volume Mount (Recommended)
```bash
# Copy trained model to server
scp -r models/bale-legal-lora-v7 user@server:/opt/bale/models/

# Update docker-compose with volume
volumes:
  - /opt/bale/models:/app/models
```

### Option 2: Bake into Image
```dockerfile
# Add to Dockerfile.api
COPY models/bale-legal-lora-v7 /app/models/bale-legal-lora-v7
```

### Option 3: Mistral API Fallback
```env
# .env - No local model needed
MISTRAL_API_KEY=your_key_here
V7_USE_API=true
```

---

## 🔧 Configuration

### Required Environment Variables
```env
# Database
POSTGRES_USER=bale
POSTGRES_PASSWORD=<strong_password>
POSTGRES_DB=bale
DATABASE_URL=postgresql://bale:<password>@postgres:5432/bale

# Redis
REDIS_URL=redis://redis:6379/0

# Security
BALE_SECRET_KEY=<generate_with_openssl>
BALE_ENV=production

# V7 Model
V7_ADAPTER_PATH=/app/models/bale-legal-lora-v7

# Optional: External LLM
MISTRAL_API_KEY=<your_key>
LOCAL_LLM_ENDPOINT=http://ollama:11434/v1/chat/completions
```

### Generate Secret Key
```bash
openssl rand -hex 32
```

---

## 🐳 Build Commands

### Build All Images
```bash
# Development
docker-compose build

# Production (with caching)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
```

### Build Individual Services
```bash
# API with V7 support
docker build -f Dockerfile.api -t bale-api:latest .

# Frontend production build
docker build -f frontend/Dockerfile.prod -t bale-frontend:latest ./frontend
```

---

## 🔒 SSL/TLS Setup

### Using Let's Encrypt (Recommended)
```bash
# Install certbot
apt install certbot python3-certbot-nginx

# Generate certificate
certbot certonly --webroot -w /var/www/certbot -d yourdomain.com

# Copy to nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

### Enable HTTPS in nginx.conf
Uncomment the HTTPS server block in `nginx/nginx.conf`.

---

## 📊 Monitoring

### Health Checks
```bash
# API health
curl http://localhost/api/health

# V7 model status
curl http://localhost/api/v5/status

# Full stack
curl http://localhost/health
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api
```

### Metrics
```bash
curl http://localhost/metrics  # Prometheus format
```

---

## 🔄 Updates & Scaling

### Deploy Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Scale API Workers
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=3
```

### Database Migrations
```bash
docker-compose exec api alembic upgrade head
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|:------|:---------|
| V7 model not loading | Check `V7_ADAPTER_PATH` and volume mount |
| MLX not available | Use Mistral API fallback (set `MISTRAL_API_KEY`) |
| Database connection fails | Verify `DATABASE_URL` and postgres health |
| Frontend 502 | Wait for api to start, check nginx upstream |
| CORS errors | Add frontend URL to `CORS_ORIGINS` |

### Reset Everything
```bash
docker-compose down -v  # WARNING: Deletes data
docker-compose up -d
```

---

## 📁 File Structure

```
BALE-project/
├── Dockerfile.api          # API with V7 support
├── frontend/
│   ├── Dockerfile         # Development
│   └── Dockerfile.prod    # Production multi-stage
├── docker-compose.yml      # Base services
├── docker-compose.prod.yml # Production overrides
├── nginx/
│   ├── nginx.conf         # Reverse proxy config
│   └── ssl/               # SSL certificates
└── models/
    └── bale-legal-lora-v7/ # V7 model adapters
```

# BALE Deployment Guide
This guide covers deploying BALE to production environments.
---
## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [LLM Configuration](#llm-configuration)
7. [SSL/TLS Setup](#ssltls-setup)
8. [Monitoring](#monitoring)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)
---
## Prerequisites
### Hardware Requirements
| Component | Minimum | Recommended |
|:----------|:--------|:------------|
| CPU | 4 cores | 8+ cores |
| RAM | 16 GB | 32+ GB |
| Storage | 50 GB SSD | 200+ GB NVMe |
| GPU | - | A100 40GB (for local LLM) |
### Software Requirements
- Docker 24.0+
- Docker Compose 2.20+
- PostgreSQL 15+
- Redis 7+
- Neo4j 5+ (optional)
- Python 3.11+ (for direct deployment)
- Node.js 20+ (for frontend)
---
## Docker Deployment
### Quick Start
```bash
# Clone repository
git clone https://github.com/yourorg/bale-project.git
cd bale-project
# Configure environment
cp .env.example .env
# Edit .env with production values
# Start all services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
# Run migrations
docker-compose exec api alembic upgrade head
# Verify deployment
curl http://localhost:8080/health
```
### Production Compose
Create `docker-compose.prod.yml`:
```yaml
version: '3.8'
services:
api:
restart: always
environment:
- BALE_ENV=production
- BALE_DEBUG=false
deploy:
replicas: 3
resources:
limits:
cpus: '2'
memory: 4G
healthcheck:
test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
interval: 30s
timeout: 10s
retries: 3
frontend:
restart: always
environment:
- NODE_ENV=production
postgres:
restart: always
volumes:
- /data/postgres:/var/lib/postgresql/data
environment:
- POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
redis:
restart: always
command: redis-server --appendonly yes
volumes:
- /data/redis:/data
```
### Build & Push Images
```bash
# Build images
docker build -t bale/api:latest -f Dockerfile.api .
docker build -t bale/frontend:latest -f frontend/Dockerfile frontend/
# Tag for registry
docker tag bale/api:latest your-registry.com/bale/api:v2.2.0
docker tag bale/frontend:latest your-registry.com/bale/frontend:v2.2.0
# Push
docker push your-registry.com/bale/api:v2.2.0
docker push your-registry.com/bale/frontend:v2.2.0
```
---
## Kubernetes Deployment
### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
name: bale
```
### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
name: bale-api
namespace: bale
spec:
replicas: 3
selector:
matchLabels:
app: bale-api
template:
metadata:
labels:
app: bale-api
spec:
containers:
- name: api
image: your-registry.com/bale/api:v2.2.0
ports:
- containerPort: 8080
env:
- name: DATABASE_URL
valueFrom:
secretKeyRef:
name: bale-secrets
key: database-url
- name: REDIS_URL
valueFrom:
secretKeyRef:
name: bale-secrets
key: redis-url
resources:
requests:
memory: "1Gi"
cpu: "500m"
limits:
memory: "4Gi"
cpu: "2"
livenessProbe:
httpGet:
path: /health
port: 8080
initialDelaySeconds: 10
periodSeconds: 30
readinessProbe:
httpGet:
path: /health
port: 8080
initialDelaySeconds: 5
periodSeconds: 10
```
### Service
```yaml
apiVersion: v1
kind: Service
metadata:
name: bale-api
namespace: bale
spec:
selector:
app: bale-api
ports:
- port: 80
targetPort: 8080
type: ClusterIP
```
### Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
name: bale-ingress
namespace: bale
annotations:
kubernetes.io/ingress.class: nginx
cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
tls:
- hosts:
- api.bale.example.com
secretName: bale-tls
rules:
- host: api.bale.example.com
http:
paths:
- path: /
pathType: Prefix
backend:
service:
name: bale-api
port:
number: 80
```
---
## Environment Configuration
### Required Variables
```env
# Application
BALE_ENV=production
BALE_DEBUG=false
BALE_SECRET_KEY=<generate-with-openssl-rand-hex-32>
# Database
DATABASE_URL=postgresql://user:pass@host:5432/bale
POSTGRES_PASSWORD=<strong-password>
# Redis
REDIS_URL=redis://:password@host:6379/0
# LLM
LOCAL_LLM_ENDPOINT=http://ollama:11434/v1/chat/completions
LOCAL_LLM_MODEL=qwen2.5:32b
MISTRAL_API_KEY=<your-api-key>
# Neo4j (Legacy/Enterprise only)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<password>
# API
API_PORT=8080
CORS_ORIGINS=https://app.bale.example.com
```
### Secrets Management
For Kubernetes, use sealed secrets or external secret operators:
```bash
kubectl create secret generic bale-secrets \
--from-literal=database-url='postgresql://...' \
--from-literal=redis-url='redis://...' \
--from-literal=secret-key='...' \
-n bale
```
---
## Database Setup
### PostgreSQL
```sql
-- Create database and user
CREATE USER bale WITH PASSWORD 'your_password';
CREATE DATABASE bale OWNER bale;
-- Enable extensions
\c bale
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```
### Migrations
```bash
# Run all pending migrations
alembic upgrade head
# Rollback one step
alembic downgrade -1
# Generate new migration
alembic revision --autogenerate -m "Description"
```
### Backups
```bash
# Backup
pg_dump -h localhost -U bale -d bale > backup_$(date +%Y%m%d).sql
# Restore
psql -h localhost -U bale -d bale < backup_20260116.sql
```
---
## LLM Configuration
### Option 1: Local LLM (Ollama)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
# Pull model
ollama pull qwen2.5:32b
# Run with GPU
OLLAMA_NUM_GPU=1 ollama serve
```
### Option 2: Cloud API (Mistral)
Set in environment:
```env
MISTRAL_API_KEY=your_key_here
EXECUTION_MODE=mistral
```
### Option 3: vLLM (High Performance)
```bash
# Run vLLM server
python -m vllm.entrypoints.openai.api_server \
--model Qwen/Qwen2.5-32B-Instruct \
--tensor-parallel-size 4
```
---
## SSL/TLS Setup
### Nginx Reverse Proxy
```nginx
server {
listen 443 ssl http2;
server_name api.bale.example.com;
ssl_certificate /etc/letsencrypt/live/api.bale.example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/api.bale.example.com/privkey.pem;
location / {
proxy_pass http://localhost:8080;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
}
location /ws {
proxy_pass http://localhost:8080;
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
}
}
```
---
## Monitoring
### Health Endpoints
```
GET /health # Basic health check
GET /health/ready # Readiness (includes DB check)
GET /health/live # Liveness
```
### Prometheus Metrics
```yaml
# prometheus.yml
scrape_configs:
- job_name: 'bale-api'
static_configs:
- targets: ['bale-api:8080']
metrics_path: /metrics
```
### Grafana Dashboard
Import the included dashboard from `monitoring/grafana-dashboard.json`.
### Alerting
```yaml
# alertmanager rules
groups:
- name: bale
rules:
- alert: HighErrorRate
expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
for: 5m
labels:
severity: critical
```
---
## Backup & Recovery
### Automated Backups
```bash
#!/bin/bash
# backup.sh - Run daily via cron
DATE=$(date +%Y%m%d)
BACKUP_DIR=/backups
# PostgreSQL
pg_dump -h localhost -U bale bale | gzip > $BACKUP_DIR/postgres_$DATE.sql.gz
# Redis
redis-cli BGSAVE
cp /data/redis/dump.rdb $BACKUP_DIR/redis_$DATE.rdb
# Upload to S3
aws s3 cp $BACKUP_DIR/ s3://bale-backups/$DATE/ --recursive
# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -mtime +30 -delete
```
### Disaster Recovery
1. Restore PostgreSQL from backup
2. Restore Redis dump
3. Redeploy containers
4. Verify with health checks
5. Re-run any failed migrations
---
## Troubleshooting
### Common Issues
**API not starting:**
```bash
# Check logs
docker-compose logs api -f
# Verify database connection
docker-compose exec api python -c "from database.config import check_connection; print(check_connection())"
```
**High memory usage:**
```bash
# Check for memory leaks
docker stats bale-api
# Restart with limits
docker-compose up -d --force-recreate api
```
**LLM timeouts:**
```env
# Increase timeout in .env
LLM_TIMEOUT=300
```
### Support
- GitHub Issues: https://github.com/yourorg/bale-project/issues
- Documentation: https://docs.bale.example.com
- Email: support@bale.example.com

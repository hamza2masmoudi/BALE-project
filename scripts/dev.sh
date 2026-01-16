#!/usr/bin/env bash
# BALE Development Startup Script
# Starts all required services and the API

set -e

echo "🚀 Starting BALE Development Environment..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "   Edit .env with your configuration before continuing."
    echo ""
fi

# Source environment
set -a
source .env
set +a

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi

# Start infrastructure
echo "🐘 Starting PostgreSQL, Redis, Neo4j..."
docker-compose up -d postgres redis neo4j

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check PostgreSQL
echo -n "   PostgreSQL: "
if docker-compose exec -T postgres pg_isready -U bale > /dev/null 2>&1; then
    echo "✅"
else
    echo "⏳ (waiting...)"
    sleep 5
fi

# Check Redis
echo -n "   Redis: "
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅"
else
    echo "⏳ (waiting...)"
fi

echo ""

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate and install
source .venv/bin/activate

echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Run migrations
echo "🗃️  Running database migrations..."
alembic upgrade head 2>/dev/null || echo "   (No pending migrations)"

# Run startup checks
echo ""
python -c "from src.startup import run_startup_checks; run_startup_checks()"

# Seed demo data if requested
if [ "$1" == "--seed" ]; then
    echo "🌱 Seeding demo data..."
    python scripts/seed_demo.py
fi

# Start API
echo ""
echo "🌐 Starting BALE API on http://localhost:${API_PORT:-8080}"
echo "   Docs: http://localhost:${API_PORT:-8080}/docs"
echo ""
echo "Press Ctrl+C to stop."
echo ""

uvicorn api.main:app --host 0.0.0.0 --port ${API_PORT:-8080} --reload

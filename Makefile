# BALE Makefile
# Common development and deployment commands

.PHONY: help install dev test lint build deploy clean

# Default target
help:
	@echo "BALE Development Commands"
	@echo "========================="
	@echo ""
	@echo "  make install     Install all dependencies"
	@echo "  make dev         Start development environment"
	@echo "  make test        Run test suite"
	@echo "  make lint        Run linters"
	@echo "  make build       Build Docker images"
	@echo "  make deploy      Deploy to production"
	@echo "  make clean       Clean build artifacts"
	@echo ""

# Install dependencies
install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	cd frontend && npm install

# Start development environment
dev:
	./scripts/dev.sh

# Start with demo data
dev-seed:
	./scripts/dev.sh --seed

# Run tests
test:
	pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=src --cov=api --cov-report=html --cov-report=term

# Lint code
lint:
	ruff check src/ api/ --fix
	mypy src/ api/ --ignore-missing-imports

# Format code
format:
	ruff format src/ api/

# Build Docker images
build:
	docker-compose build

# Build production images
build-prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start services
up:
	docker-compose up -d

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Run database migrations
migrate:
	alembic upgrade head

# Create new migration
migration:
	@read -p "Migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

# Seed demo data
seed:
	python scripts/seed_demo.py

# Start API only (no Docker)
api:
	uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload

# Start frontend only
frontend:
	cd frontend && npm run dev

# Run startup checks
check:
	python -c "from src.startup import run_startup_checks; run_startup_checks()"

# Generate API client types
gen-types:
	@echo "TypeScript types are in frontend/src/api/client.ts"

# Deploy to production
deploy:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "Deployed! Check health at /health"

# Clean build artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .coverage coverage.xml 2>/dev/null || true

# Reset database
db-reset:
	docker-compose exec postgres psql -U bale -d bale -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	alembic upgrade head

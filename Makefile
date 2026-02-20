# ===========================================
# Salon Flow - Development Commands
# ===========================================

.PHONY: help install dev test lint format clean docker-up docker-down seed

# Default target
help:
@echo "Salon Flow - Available Commands:"
@echo ""
@echo "  make install        Install all dependencies"
@echo "  make dev            Start development environment"
@echo "  make test           Run all tests"
@echo "  make lint           Run linting checks"
@echo "  make format         Format all code"
@echo "  make clean          Clean build artifacts"
@echo "  make docker-up      Start Docker services"
@echo "  make docker-down    Stop Docker services"
@echo "  make seed           Seed database with test data"
@echo "  make migrate        Run database migrations"
@echo "  make docs           Generate API documentation"
@echo ""

# ===========================================
# Installation
# ===========================================
install:
@echo "Installing Python dependencies..."
cd services/api && pip install -r requirements.txt
cd services/ai && pip install -r requirements.txt
cd services/notification && pip install -r requirements.txt
@echo "Installing Node.js dependencies..."
cd apps/client && npm install
cd apps/staff && npm install
cd apps/manager && npm install
cd apps/owner && npm install
@echo "Installing pre-commit hooks..."
pre-commit install
@echo "✅ Installation complete!"

# ===========================================
# Development
# ===========================================
dev:
@echo "Starting development environment..."
docker-compose up -d
@echo "Waiting for services to be ready..."
@sleep 10
@echo "✅ Development environment ready!"
@echo "API: http://localhost:8000"
@echo "Client PWA: http://localhost:3000"
@echo "Staff PWA: http://localhost:3001"
@echo "Manager PWA: http://localhost:3002"
@echo "Owner PWA: http://localhost:3003"
@echo "Firebase UI: http://localhost:4000"

dev-logs:
docker-compose logs -f

# ===========================================
# Docker
# ===========================================
docker-up:
docker-compose up -d

docker-down:
docker-compose down

docker-build:
docker-compose build

docker-clean:
docker-compose down -v --remove-orphans

# ===========================================
# Testing
# ===========================================
test:
@echo "Running Python tests..."
pytest tests/ -v --cov=services --cov-report=html
@echo "Running frontend tests..."
cd apps/client && npm test
cd apps/staff && npm test
cd apps/manager && npm test
cd apps/owner && npm test

test-api:
pytest tests/api/ -v

test-ai:
pytest tests/ai/ -v

test-e2e:
npx playwright test

test-coverage:
pytest tests/ -v --cov=services --cov-report=html --cov-report=term
@echo "Coverage report: htmlcov/index.html"

# ===========================================
# Linting
# ===========================================
lint:
@echo "Linting Python code..."
black --check services/
isort --check-only services/
mypy services/
ruff check services/
@echo "Linting frontend code..."
cd apps/client && npm run lint
cd apps/staff && npm run lint
cd apps/manager && npm run lint
cd apps/owner && npm run lint

lint-fix:
@echo "Fixing linting issues..."
black services/
isort services/
ruff check --fix services/
cd apps/client && npm run lint --fix
cd apps/staff && npm run lint --fix
cd apps/manager && npm run lint --fix
cd apps/owner && npm run lint --fix

# ===========================================
# Formatting
# ===========================================
format:
@echo "Formatting Python code..."
black services/
isort services/
@echo "Formatting frontend code..."
cd apps/client && npm run format
cd apps/staff && npm run format
cd apps/manager && npm run format
cd apps/owner && npm run format

# ===========================================
# Database
# ===========================================
seed:
@echo "Seeding database with test data..."
python scripts/seed_db.py
@echo "✅ Database seeded!"

migrate:
@echo "Running database migrations..."
python scripts/migrate.py

reset-db:
@echo "Resetting database..."
docker-compose down -v
docker-compose up -d firebase-emulator
@sleep 5
python scripts/seed_db.py

# ===========================================
# Documentation
# ===========================================
docs:
@echo "Generating API documentation..."
cd services/api && python -c "import main; print('API docs at /docs')"
@echo "Open http://localhost:8000/docs for Swagger UI"

docs-build:
python scripts/generate_docs.py

# ===========================================
# Cleanup
# ===========================================
clean:
@echo "Cleaning build artifacts..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name ".coverage" -delete
find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
@echo "✅ Cleanup complete!"

# ===========================================
# CI/CD
# ===========================================
ci: install lint test

ci-build:
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# ===========================================
# Utilities
# ===========================================
check-env:
@echo "Checking environment variables..."
@test -f .env && echo "✅ .env exists" || echo "❌ .env missing - copy from .env.example"
@echo "Required: OPENROUTER_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN"

logs:
docker-compose logs -f --tail=100

ps:
docker-compose ps

restart:
docker-compose restart

#!/bin/bash
# ===========================================
# Salon Flow - Development Setup Script
# ===========================================

set -e

echo "🚀 Setting up Salon Flow development environment..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "  ${GREEN}✓${NC} Python: $PYTHON_VERSION"
else
    echo -e "  ${RED}✗${NC} Python not found"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "  ${GREEN}✓${NC} Node.js: $NODE_VERSION"
else
    echo -e "  ${RED}✗${NC} Node.js not found"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "  ${GREEN}✓${NC} Docker: $DOCKER_VERSION"
else
    echo -e "  ${YELLOW}!${NC} Docker not found (optional for local dev)"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "  ${GREEN}✓${NC} Docker Compose: $COMPOSE_VERSION"
else
    echo -e "  ${YELLOW}!${NC} Docker Compose not found (optional for local dev)"
fi

echo ""

# Setup environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo -e "  ${GREEN}✓${NC} .env created"
else
    echo -e "  ${YELLOW}!${NC} .env already exists"
fi

# Setup Python virtual environment
echo ""
echo "🐍 Setting up Python environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "  ${GREEN}✓${NC} Virtual environment created"
else
    echo -e "  ${YELLOW}!${NC} Virtual environment already exists"
fi

# Activate venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
for service in api ai notification; do
    if [ -f "services/$service/requirements.txt" ]; then
        pip install -r services/$service/requirements.txt -q
        echo -e "  ${GREEN}✓${NC} $service dependencies installed"
    fi
done

# Install dev dependencies
pip install pytest pytest-asyncio pytest-cov black isort ruff mypy faker -q
echo -e "  ${GREEN}✓${NC} Development dependencies installed"

# Setup frontend dependencies
echo ""
echo "📦 Setting up frontend dependencies..."

for app in client staff manager owner; do
    if [ -d "apps/$app" ]; then
        echo "Installing $app dependencies..."
        cd apps/$app
        npm install --silent
        echo -e "  ${GREEN}✓${NC} $app dependencies installed"
        cd ../..
    fi
done

# Install pre-commit hooks
echo ""
echo "🔧 Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo -e "  ${GREEN}✓${NC} Pre-commit hooks installed"
else
    pip install pre-commit -q
    pre-commit install
    echo -e "  ${GREEN}✓${NC} Pre-commit installed and configured"
fi

# Create test directories
echo ""
echo "📁 Creating test directories..."
mkdir -p tests/api tests/ai tests/notification tests/e2e tests/fixtures
touch tests/__init__.py tests/api/__init__.py tests/ai/__init__.py
echo -e "  ${GREEN}✓${NC} Test directories created"

# Generate mock data
echo ""
echo "🎲 Generating mock data..."
python scripts/generate_mock.py all -c 20 -o tests/fixtures

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}✅ Development setup complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Run 'make dev' to start services"
echo "  3. Run 'make test' to run tests"
echo "  4. Run 'make seed' to seed database"
echo ""
echo "Available commands:"
echo "  make help        - Show all commands"
echo "  make dev         - Start development environment"
echo "  make test        - Run all tests"
echo "  make lint        - Run linting"
echo "  make format      - Format code"
echo ""

# Contributing to Salon Flow

Thank you for your interest in contributing to Salon Flow! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)

---

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

---

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git
- GCP Account (for cloud deployment)

### Local Development

```bash
# Clone the repository
git clone https://github.com/Akram0307/salon-flow.git
cd salon-flow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r services/api/requirements.txt
pip install -r services/ai/requirements.txt

# Install frontend dependencies
cd apps/owner && npm install && cd ../..

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Start local development
make dev
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test suites
make test-backend
make test-ai
make test-frontend

# Run with coverage
make coverage
```

---

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/Akram0307/salon-flow/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Environment details

### Suggesting Features

1. Open a discussion in [GitHub Discussions](https://github.com/Akram0307/salon-flow/discussions)
2. Describe the feature and its use case
3. Explain why it would benefit the project

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes
6. Push to your fork
7. Open a Pull Request

---

## Pull Request Process

1. **Ensure all tests pass** - Run `make test` before submitting
2. **Update documentation** - Update README.md and docs/ if needed
3. **Follow coding standards** - See below
4. **Write meaningful commit messages** - See below
5. **Request review** - Tag relevant reviewers

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No sensitive data in commits

---

## Coding Standards

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints for all functions
- Write docstrings for classes and public methods
- Maximum line length: 100 characters

```python
def get_customer(customer_id: str, salon_id: str) -> Customer:
    """Retrieve a customer by ID within a salon context.
    
    Args:
        customer_id: The unique customer identifier
        salon_id: The salon identifier for multi-tenant isolation
        
    Returns:
        Customer object with all details
        
    Raises:
        NotFoundError: If customer doesn't exist
    """
    pass
```

### TypeScript/React

- Use TypeScript strict mode
- Follow [Airbnb Style Guide](https://github.com/airbnb/javascript)
- Use functional components with hooks
- Props interfaces should be named `ComponentNameProps`

```typescript
interface BookingCardProps {
  booking: Booking;
  onStatusChange: (id: string, status: BookingStatus) => void;
}

export const BookingCard: React.FC<BookingCardProps> = ({ 
  booking, 
  onStatusChange 
}) => {
  // Component implementation
};
```

### File Naming

- Python: `snake_case.py`
- TypeScript: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- Tests: `test_*.py` or `*.test.ts`

---

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style (formatting, etc.) |
| `refactor` | Code refactoring |
| `test` | Adding/updating tests |
| `chore` | Maintenance tasks |
| `perf` | Performance improvement |

### Examples

```
feat(booking): add WhatsApp booking integration

fix(auth): resolve JWT token refresh issue

docs(api): update OpenAPI documentation

test(customers): add loyalty points test cases
```

---

## Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions

---

## Questions?

- Open a [Discussion](https://github.com/Akram0307/salon-flow/discussions)
- Email: support@salonflow.ai

Thank you for contributing! 🎉

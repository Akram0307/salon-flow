# Git Workflow - Salon_Flow

## Branch Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/description` | `feature/booking-calendar-views` |
| Bug Fix | `bugfix/description` | `bugfix/login-redirect-loop` |
| Hot Fix | `hotfix/description` | `hotfix/payment-processing` |
| Documentation | `docs/description` | `docs/api-endpoint-updates` |
| Refactoring | `refactor/description` | `refactor/auth-service` |

## Commit Message Format

Follow Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semi-colons, etc)
- **refactor**: Code refactoring without feature changes
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Build process, dependencies, tooling

### Examples
```
feat(booking): add recurring appointment support

Implement weekly and monthly recurring bookings with
conflict detection and staff availability checks.

Closes #123
```

```
fix(auth): resolve JWT token expiration edge case

Tokens were not being refreshed when expiry was within
5 minutes of the request. Added buffer time check.

Fixes #456
```

## Pull Request Process

1. **Create Feature Branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes** following coding standards

3. **Run Tests** before pushing
   ```bash
   # Backend tests
   pytest tests/ -v
   
   # E2E tests
   npx playwright test
   ```

4. **Commit Changes** with conventional commit messages

5. **Push Branch** to remote
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request** via GitHub
   - Add descriptive title
   - Include summary of changes
   - Link related issues
   - Add reviewers

7. **Code Review** requirements
   - Minimum 1 approval required
   - All comments must be resolved
   - CI/CD checks must pass

8. **Merge** using Squash Merge
   - Ensure commit message follows conventions
   - Delete branch after merge

## CI/CD Pipeline

### GitHub Actions Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test.yml` | Pull Request | Run all tests, linting |
| `lint.yml` | Pull Request | Code quality checks |
| `deploy.yml` | Merge to main | Deploy to staging |
| `deploy-cloudrun.yml` | Release tag | Deploy to production |

### Test Gates
All PRs must pass:
- ✅ pytest (backend API tests)
- ✅ pytest (AI service tests)
- ✅ Playwright E2E tests (critical paths)
- ✅ Code coverage threshold (80%)
- ✅ Linting checks

## Pre-commit Checklist

Before creating a PR, verify:
- [ ] All tests pass locally
- [ ] Code follows style guide
- [ ] No console.log statements in production code
- [ ] TypeScript types are properly defined
- [ ] Python type hints are included
- [ ] Documentation updated (if needed)
- [ ] Environment variables documented

## Release Process

1. **Version Bump** in package files
2. **Update CHANGELOG.md** with release notes
3. **Create Release Tag** (e.g., `v1.2.3`)
4. **Deploy to Production** via GitHub Actions
5. **Monitor** deployment metrics and errors

## Git Best Practices

### Do's
- ✅ Keep commits atomic and focused
- ✅ Write descriptive commit messages
- ✅ Pull latest changes before starting work
- ✅ Use meaningful branch names
- ✅ Delete merged branches
- ✅ Squash merge feature branches

### Don'ts
- ❌ Commit directly to `main`
- ❌ Include large binary files
- ❌ Commit sensitive data (API keys, passwords)
- ❌ Leave merge conflicts unresolved
- ❌ Force push to shared branches

## Conflict Resolution

When encountering merge conflicts:
1. Pull latest changes: `git pull origin main`
2. Identify conflicting files
3. Resolve conflicts manually
4. Test changes locally
5. Commit resolved files
6. Push updated branch

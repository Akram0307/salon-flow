# CI/CD Pipeline Skill

## Overview
Set up automated CI/CD pipelines using GitHub Actions for testing and deployment.

## Pipeline Structure
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: pytest --cov=app tests/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
      - uses: google-github-actions/deploy-cloudrun@v2
```

## Pipeline Stages

| Stage | Trigger | Actions |
|-------|---------|--------|
| Test | Every push | Lint, unit tests, coverage |
| Build | main branch | Build Docker image |
| Deploy Staging | develop branch | Deploy to staging |
| Deploy Production | main branch | Deploy to production |

## Deployment Strategy
- Blue-green deployment for zero downtime
- Automatic rollback on failure
- Slack notifications on deployment

# Code Review Skill

## Overview
Structured code review process for Salon_Flow. Ensure code quality, security, and maintainability through systematic review.

## Philosophy
> "Code is read more often than it is written. Code review is not about finding faults, it's about improving quality."

## Review Types

### Pre-Merge Review
Required before merging to main branch.

### Post-Implementation Review
After feature completion for learning and improvement.

### Security Review
For changes involving auth, payments, or sensitive data.

## Review Checklist

### Functionality
```markdown
- [ ] Code does what it's supposed to do
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] No obvious bugs
```

### Code Quality
```markdown
- [ ] Code is readable and self-documenting
- [ ] Functions/methods are focused and small
- [ ] No code duplication (DRY principle)
- [ ] Naming is clear and consistent
- [ ] Comments explain "why" not "what"
```

### Testing
```markdown
- [ ] Unit tests cover new code
- [ ] Tests are meaningful (not just coverage)
- [ ] Edge cases are tested
- [ ] Tests are maintainable
```

### Security
```markdown
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] Output encoding applied
- [ ] Auth checks in place
- [ ] Tenant isolation maintained
```

### Performance
```markdown
- [ ] No N+1 queries
- [ ] Appropriate data structures
- [ ] Caching considered
- [ ] No memory leaks
```

### Salon Context
```markdown
- [ ] Multi-tenant data isolation
- [ ] Timezone handling correct
- [ ] Offline-first considerations
- [ ] Mobile-responsive UI
- [ ] Accessibility (a11y) standards
```

## Review Process

### 1. Request Review
```markdown
## Pull Request: [Feature Name]

### Summary
[What does this PR do?]

### Changes
- Change 1
- Change 2

### Testing
- [ ] Unit tests added
- [ ] Manual testing done
- [ ] E2E tests passing

### Screenshots
[If UI changes]

### Checklist
- [ ] Self-reviewed code
- [ ] Tests passing
- [ ] No new warnings
- [ ] Documentation updated
```

### 2. Review Code

**Review Order:**
1. Understand the intent (read PR description)
2. Review the design/architecture
3. Review the implementation
4. Review the tests
5. Review the documentation

**Review Focus Areas:**

| Priority | Focus Area |
|----------|------------|
| 🔴 High | Security, data integrity, multi-tenant isolation |
| 🟠 Medium | Performance, error handling, edge cases |
| 🟡 Low | Style, naming, minor optimizations |

### 3. Provide Feedback

**Feedback Format:**
```markdown
## Review Comments

### 🔴 Must Fix
[Issues that must be addressed before merge]

### 🟠 Should Consider
[Suggestions that would improve the code]

### 💡 Nitpicks
[Minor style or preference comments]

### ✅ Good Stuff
[Positive feedback on good practices]
```

**Comment Template:**
```markdown
**Issue:** [Description of the issue]
**Location:** [File:line]
**Suggestion:** [How to fix it]
**Reason:** [Why it matters]
```

### 4. Respond to Review

When receiving feedback:
```markdown
- Address all comments
- Mark resolved issues
- Explain if you disagree (politely)
- Request re-review after changes
```

## Salon-Specific Review Points

### Multi-Tenant Isolation
```python
# ❌ Bad - No tenant filter
def get_bookings():
    return db.query(Booking).all()

# ✅ Good - Tenant filtered
def get_bookings(tenant_id: str):
    return db.query(Booking).filter(Booking.tenant_id == tenant_id).all()
```

### Timezone Handling
```python
# ❌ Bad - Naive datetime
appointment.time = datetime.now()

# ✅ Good - Timezone aware
appointment.time = datetime.now(timezone.utc)
```

### Payment Security
```python
# ❌ Bad - Logging sensitive data
logger.info(f"Payment: {credit_card}")

# ✅ Good - Masked logging
logger.info(f"Payment: ****{last_four}")
```

## Anti-Patterns to Avoid

❌ Rubber stamping (approving without review)
❌ Nitpicking excessively
❌ Being rude or dismissive
❌ Reviewing too much at once
❌ Ignoring the PR description
❌ Focusing only on style

## Best Practices

✅ Review in small batches (<400 lines)
✅ Be constructive and specific
✅ Explain the "why" behind suggestions
✅ Distinguish between must-fix and nice-to-have
✅ Acknowledge good code
✅ Respond promptly to review requests
✅ Use code suggestions when possible

## Review Metrics

Track for continuous improvement:

| Metric | Target |
|--------|--------|
| Time to first review | < 4 hours |
| Review iterations | < 3 |
| Defects found in review | Increasing |
| Defects in production | Decreasing |

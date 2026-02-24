# Writing Plans Skill

## Overview
Create detailed implementation plans for Salon_Flow features. Break complex work into bite-sized, verifiable tasks.

## Philosophy
> "A good plan violently executed now is better than a perfect plan next week."

## Planning Process

### Phase 1: Understand the Scope
```
1. What is the feature/fix being implemented?
2. What are the acceptance criteria?
3. What are the constraints (time, resources, dependencies)?
4. What is the definition of done?
```

### Phase 2: Identify Components
```
1. Frontend changes needed?
2. Backend changes needed?
3. Database changes needed?
4. External integrations?
5. Testing requirements?
```

### Phase 3: Break Down Tasks
```
1. What is the smallest deliverable unit?
2. What are the dependencies between tasks?
3. What can be done in parallel?
4. What are the checkpoints?
5. How do we verify each task?
```

### Phase 4: Sequence & Estimate
```
1. What is the optimal order?
2. What are the risk points?
3. What is the time estimate?
4. What are the rollback points?
```

## Plan Template

```markdown
# Implementation Plan: [Feature Name]

## Summary
[One paragraph description]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Design

### Architecture
[Diagram or description]

### Data Model
[Schema changes if any]

### API Changes
[New/modified endpoints]

### UI Changes
[Screens/components affected]

## Task Breakdown

### Phase 1: Foundation
| Task | Description | Est. | Status |
|------|-------------|------|--------|
| T1.1 | [Task description] | 30m | ⬜ |
| T1.2 | [Task description] | 1h | ⬜ |

### Phase 2: Core Implementation
| Task | Description | Est. | Status |
|------|-------------|------|--------|
| T2.1 | [Task description] | 2h | ⬜ |
| T2.2 | [Task description] | 1h | ⬜ |

### Phase 3: Integration & Testing
| Task | Description | Est. | Status |
|------|-------------|------|--------|
| T3.1 | [Task description] | 1h | ⬜ |
| T3.2 | [Task description] | 30m | ⬜ |

## Dependencies
- Dependency 1
- Dependency 2

## Risks & Mitigations
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Risk 1 | Medium | High | Mitigation strategy |

## Rollback Plan
[How to revert if something goes wrong]

## Verification Checklist
- [ ] All acceptance criteria met
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing complete
- [ ] Code review approved
- [ ] Documentation updated
```

## Salon Context Examples

### Example: Loyalty Points Feature

```markdown
# Implementation Plan: Loyalty Points System

## Summary
Implement a points-based loyalty program where clients earn points for services and can redeem them for discounts.

## Acceptance Criteria
- [ ] Clients earn 1 point per $1 spent
- [ ] Points can be redeemed at checkout
- [ ] Owner can configure point value
- [ ] Points expire after 12 months
- [ ] Points history visible to client

## Task Breakdown

### Phase 1: Data Model
| Task | Description | Est. | Status |
|------|-------------|------|--------|
| T1.1 | Create LoyaltyPoints model | 30m | ⬜ |
| T1.2 | Create PointsTransaction model | 30m | ⬜ |
| T1.3 | Add loyalty_settings to Tenant | 20m | ⬜ |

### Phase 2: Backend API
| Task | Description | Est. | Status |
|------|-------------|------|--------|
| T2.1 | POST /loyalty/earn endpoint | 1h | ⬜ |
| T2.2 | POST /loyalty/redeem endpoint | 1h | ⬜ |
| T2.3 | GET /loyalty/balance endpoint | 30m | ⬜ |
| T2.4 | GET /loyalty/history endpoint | 30m | ⬜ |

### Phase 3: Frontend
| Task | Description | Est. | Status |
|------|-------------|------|--------|
| T3.1 | Loyalty settings page (owner) | 2h | ⬜ |
| T3.2 | Points display at checkout | 1h | ⬜ |
| T3.3 | Points history page (client) | 1h | ⬜ |

### Phase 4: Integration
| Task | Description | Est. | Status |
|------|-------------|------|--------|
| T4.1 | Integrate with booking completion | 1h | ⬜ |
| T4.2 | Integrate with payment flow | 1h | ⬜ |
| T4.3 | Add expiration cron job | 30m | ⬜ |
```

## Task Sizing Guide

| Size | Duration | Complexity |
|------|----------|------------|
| XS | 15-30 min | Single file, obvious change |
| S | 30-60 min | Few files, clear implementation |
| M | 1-2 hours | Multiple components, some thought needed |
| L | 2-4 hours | Significant changes, design decisions |
| XL | 4+ hours | Break down further! |

## Anti-Patterns to Avoid

❌ Tasks that are too large (>4 hours)
❌ Vague task descriptions
❌ Missing verification steps
❌ Ignoring dependencies
❌ No rollback plan
❌ Forgetting about tests

## Best Practices

✅ Each task should be independently verifiable
✅ Include test tasks in the plan
✅ Identify parallel work opportunities
✅ Plan for rollback at each checkpoint
✅ Update plan as you learn
✅ Mark tasks complete as you go

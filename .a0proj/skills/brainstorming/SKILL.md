# Brainstorming Skill

## Overview
Socratic design refinement methodology for Salon_Flow features. Before writing code, step back to understand what the user really wants to accomplish.

## Philosophy
> "The best code is no code. The second best is well-understood code."

## Process

### Phase 1: Understand the Request
```
1. What is the user asking for?
2. What problem are they trying to solve?
3. Who is the end user (owner, manager, staff, client)?
4. What is the business value?
```

### Phase 2: Explore the Domain
```
1. How does this fit into salon operations?
2. What are the edge cases?
3. What happens if it fails?
4. What data is involved?
```

### Phase 3: Refine the Solution
```
1. Is this the simplest solution?
2. Can existing features be extended?
3. What are the alternatives?
4. What would a MVP look like?
```

### Phase 4: Validate Understanding
```
1. Summarize the requirement
2. Present the proposed approach
3. Get user confirmation
4. Break into digestible chunks
```

## Socratic Questions Template

### For New Features
```markdown
- What salon role benefits from this? (owner/manager/staff/client)
- Is this a new capability or improvement to existing?
- What triggers this feature? (user action, scheduled, event)
- What is the expected outcome?
- How often will this be used?
```

### For Bug Fixes
```markdown
- What is the expected behavior?
- What is the actual behavior?
- When did this start happening?
- Can you reproduce it reliably?
- What is the impact severity?
```

### For Refactoring
```markdown
- What problem does the current code cause?
- What would success look like?
- Are there tests covering this code?
- What is the risk of change?
```

## Salon Context Examples

### Example: Booking Feature Request
```
User: "I need a double booking feature"

Socratic exploration:
1. What type of double booking? (same time, back-to-back, overlapping)
2. Is this for one stylist or multiple?
3. Should the system prevent or allow conflicts?
4. What about resource constraints (chairs, equipment)?
5. How should conflicts be resolved?

Refined understanding:
"Allow staff to book overlapping appointments for services that 
can be performed simultaneously (e.g., color processing + consultation),
with conflict warnings for resource constraints."
```

## Output Format

After brainstorming, produce:

```markdown
## Feature Specification

### Summary
[One sentence description]

### User Story
As a [role], I want [feature] so that [benefit]

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### Technical Notes
- Affected components
- Data requirements
- Integration points

### Questions for User
1. [Clarifying question]
2. [Clarifying question]
```

## Anti-Patterns to Avoid

❌ Jumping straight to implementation
❌ Assuming you understand the requirement
❌ Ignoring salon business context
❌ Over-engineering the solution
❌ Skipping validation with user

## Best Practices

✅ Always ask "why" at least 3 times
✅ Consider all 4 user roles (owner, manager, staff, client)
✅ Think about edge cases in salon operations
✅ Propose MVP before full solution
✅ Get explicit confirmation before proceeding

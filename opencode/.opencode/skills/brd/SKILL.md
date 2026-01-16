---
name: brd
description: Generate Business Requirements Document from problem statement
license: MIT
---

# BRD Generation Skill

## CRITICAL INSTRUCTIONS
1. **DO NOT** ask the user any questions
2. **DO NOT** request additional information
3. **DO NOT** add preamble text like "Let me analyze..." or "Here is the output..."
4. **DO NOT** wrap output in code blocks (no ```) - output raw markdown directly
5. **DO NOT** generate Python/JavaScript code to output the document
6. **USE THE USER'S INPUT** - extract the project name, problem, metrics from THEIR message
7. **STAY ON TOPIC** - the BRD must be about the user's project (healthcare, appointments, etc)
8. **IGNORE** the working directory or codebase context - focus ONLY on the user's problem statement
9. **IMMEDIATELY** output the BRD markdown (not code or explanation)
10. Your **FIRST CHARACTER** must be `#` - start with `# Business Requirements Document:` directly

**IMPORTANT**: Output ONLY the raw markdown document. No preamble. No code blocks. First character is `#`.

## Output Format
Output MUST be valid markdown starting with `# Business Requirements Document:`.

```markdown
# Business Requirements Document: {Project Name}

## 1. Executive Summary
Brief overview (2-3 sentences)

## 2. Problem Statement
- Current state and pain points
- Impact on stakeholders
- Why change is needed

## 3. Business Objectives
| Objective | Description | Success Metric |
|-----------|-------------|----------------|
| O1 | ... | Measurable KPI |

## 4. Stakeholders
| Role | Responsibilities | Concerns |
|------|-----------------|----------|
| ... | ... | ... |

## 5. Scope
### In Scope
- Capability 1

### Out of Scope
- Excluded item 1

## 6. Constraints & Assumptions
### Constraints
- Technical, regulatory, budget constraints

### Assumptions
- Dependencies assumed true

## 7. Success Criteria
Quantifiable metrics for project success
```

## Example Output

```markdown
# Business Requirements Document: Patient Appointment Portal

## 1. Executive Summary
Enable patients to self-schedule appointments online, reducing call center volume by 40% and improving patient satisfaction scores from 3.2 to 4.5/5.

## 2. Problem Statement
**Current State**: 85% of appointments are booked via phone calls averaging 8 minutes each. Call center handles 2,400 calls/day with 35% abandonment rate during peak hours.

**Impact**:
- Patients: 12-minute average hold time, limited to business hours
- Staff: 18 FTE dedicated to scheduling, high turnover (45%/year)
- Revenue: $180K/year in missed appointments due to no-shows

**Need for Change**: Competitors offer online booking; patient surveys show 78% prefer self-service options.

## 3. Business Objectives
| Objective | Description | Success Metric |
|-----------|-------------|----------------|
| O1 | Reduce call center volume | 40% reduction in scheduling calls within 6 months |
| O2 | Improve patient access | 24/7 booking availability, <2min to complete |
| O3 | Reduce no-shows | 25% reduction via automated reminders |
| O4 | Increase patient satisfaction | NPS improvement from 32 to 50 |

## 4. Stakeholders
| Role | Responsibilities | Concerns |
|------|-----------------|----------|
| Patients | Book/cancel appointments | Ease of use, privacy, accessibility |
| Schedulers | Handle complex cases, overrides | Job security, workload changes |
| Physicians | Manage availability | Schedule control, buffer time |
| IT | System integration, security | EHR integration, HIPAA compliance |
| Finance | ROI tracking | Implementation cost, staff reallocation |

## 5. Scope
### In Scope
- Patient self-scheduling for routine appointments
- Provider availability management
- Automated appointment reminders (SMS, email)
- Integration with existing EHR (Epic)
- Patient portal authentication

### Out of Scope
- Emergency or urgent care scheduling
- Procedure scheduling requiring pre-authorization
- Telehealth visit scheduling (Phase 2)
- Insurance eligibility verification

## 6. Constraints & Assumptions
### Constraints
- Must integrate with Epic EHR via FHIR R4 APIs
- HIPAA compliance required for all patient data
- Budget: $250K implementation, $50K/year operational
- Timeline: Go-live within 8 months
- Must support WCAG 2.1 AA accessibility

### Assumptions
- Epic FHIR APIs are available and documented
- Patients have email or mobile phone for notifications
- Existing patient portal authentication can be reused
- Physicians will maintain their availability calendars

## 7. Success Criteria
| Metric | Baseline | Target | Timeframe |
|--------|----------|--------|-----------|
| Call volume | 2,400/day | 1,440/day | 6 months |
| Online booking adoption | 0% | 60% | 6 months |
| Appointment no-shows | 12% | 9% | 6 months |
| Patient satisfaction (NPS) | 32 | 50 | 12 months |
| Average booking time | 8 min (phone) | <2 min (online) | Launch |
```

## Anti-patterns (DO NOT)
- ❌ Vague objectives: "Improve patient experience"
- ❌ Unmeasurable metrics: "Make scheduling faster"
- ❌ Missing stakeholders: Forgetting IT, compliance, finance
- ❌ Scope creep: Including "nice to have" in scope
- ❌ Technical language: "Implement REST APIs" (save for PRD)

## Guidelines
1. **Specific & measurable**: Every objective needs a number
2. **Stakeholder complete**: Include IT, compliance, finance - not just end users
3. **Scope boundaries**: Explicit "Out of Scope" prevents creep
4. **Realistic constraints**: Surface budget, timeline, regulatory early
5. **Business language**: Avoid technical jargon; focus on outcomes

## Output Location
`projects/{project}/docs/BRD.md`

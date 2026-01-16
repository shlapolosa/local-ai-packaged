---
name: prd
description: Generate Product Requirements Document in RPG format for Task Master
license: MIT
---

# PRD Generation Skill

## CRITICAL INSTRUCTIONS
1. **DO NOT** ask the user any questions
2. **DO NOT** request additional information
3. **DO NOT** add preamble text like "Here is the PRD..." or "Let me generate..."
4. **DO NOT** wrap output in code blocks (no ```) - output raw markdown directly
5. **DO NOT** generate Python/JavaScript code to output the document
6. **DO NOT** output JSON or todo lists - output the actual markdown document
7. **USE THE USER'S INPUT** - extract requirements, features from THEIR message
8. **STAY ON TOPIC** - the PRD must be about the user's project (healthcare, appointments, etc)
9. **IMMEDIATELY** output the PRD markdown (not code or explanation)
10. Your **FIRST CHARACTER** must be `#` - start with `# Product Requirements Document:` directly

**IMPORTANT**: Output ONLY the raw markdown document. No preamble. No code blocks. No JSON. First character is `#`.

## Output Format
Output MUST be valid markdown starting with `# Product Requirements Document:`.
Use `<!-- include: path -->` markers for large technical sections.

## Example Output

```markdown
# Product Requirements Document: Patient Appointment Portal

## 1. Overview
### Problem Statement
Patients cannot self-schedule appointments, causing 2,400 daily calls with 35% abandonment rate.

### Target Users
| Persona | Role | Key Workflows |
|---------|------|---------------|
| Patient Sarah | Working professional, 35 | Book appointment during lunch break via mobile |
| Dr. Smith | Primary care physician | Review and adjust weekly availability |
| Admin Jane | Scheduling coordinator | Handle complex cases, manage overrides |

### Success Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Online adoption | 60% of bookings | Analytics dashboard |
| Call reduction | 40% fewer calls | Call center reports |
| Booking time | <2 minutes | Session timing |

## 2. Functional Decomposition
### Capability: Appointment Scheduling
#### Feature: Search Available Slots
- **Description**: Patient searches for available appointment slots by provider, date, and visit type
- **Inputs**: Provider ID (optional), date range, visit type, patient insurance
- **Outputs**: List of available slots with provider info, location, duration
- **Behavior**: Query provider availability, filter by patient insurance, exclude blocked times, sort by earliest

#### Feature: Book Appointment
- **Description**: Patient confirms and books a selected time slot
- **Inputs**: Selected slot ID, patient ID, reason for visit, contact preferences
- **Outputs**: Confirmation number, calendar invite, reminder preferences
- **Behavior**: Validate slot still available, create appointment record, send confirmation, schedule reminders

## 3. Structural Decomposition
<!-- include: structure/modules.md -->

```
src/
├── modules/
│   ├── scheduling/
│   │   ├── scheduling.controller.ts    # POST /appointments, GET /slots
│   │   ├── scheduling.service.ts       # Business logic, availability calc
│   │   └── scheduling.repository.ts    # Appointment CRUD
│   ├── providers/
│   │   ├── providers.controller.ts     # GET /providers, availability
│   │   └── providers.service.ts        # Provider management
│   └── notifications/
│       ├── notifications.service.ts    # Email, SMS dispatch
│       └── templates/                  # Reminder templates
```

## 4. Dependency Graph
### Foundation Layer (Phase 0)
- **Database schema**: No dependencies - tables, indexes, constraints
- **Auth integration**: No dependencies - patient portal SSO

### Core Layer (Phase 1)
- **Provider service**: Depends on [Database schema]
- **Availability engine**: Depends on [Database schema, Provider service]

### Feature Layer (Phase 2)
- **Scheduling service**: Depends on [Availability engine, Provider service]
- **Booking API**: Depends on [Scheduling service, Auth integration]

### Integration Layer (Phase 3)
- **Notification service**: Depends on [Scheduling service]
- **EHR sync**: Depends on [Booking API]

## 5. Implementation Roadmap
### Phase 0: Foundation
**Goal**: Database and authentication infrastructure ready
**Entry Criteria**: Architecture approved, dev environment provisioned
**Tasks**:
- [ ] Create database schema (depends on: none)
  - Acceptance: All tables created, migrations run successfully
  - Test: Schema validation, foreign key integrity tests
- [ ] Configure auth integration (depends on: none)
  - Acceptance: SSO login works with patient portal
  - Test: Auth flow integration test

**Exit Criteria**: Database accessible, auth tokens validated
**Delivers**: Developers can connect and authenticate

### Phase 1: Core Services
**Goal**: Provider and availability services operational
**Entry Criteria**: Phase 0 complete
**Tasks**:
- [ ] Implement provider service (depends on: [Database schema])
  - Acceptance: CRUD operations for providers work
  - Test: Unit tests for provider repository
- [ ] Build availability engine (depends on: [Database schema, Provider service])
  - Acceptance: Returns correct available slots
  - Test: Unit tests with various schedule scenarios

**Exit Criteria**: GET /providers and GET /availability return valid data
**Delivers**: API consumers can query provider availability

## 6. Test Strategy
<!-- include: test-strategy.md -->

### Test Pyramid
- Unit: 70% - Service methods, validators, utilities
- Integration: 20% - API endpoints, database queries
- E2E: 10% - Booking flow, reminder delivery

### Critical Scenarios
| ID | Scenario | Type | Priority |
|----|----------|------|----------|
| TS-001 | Book available slot | E2E | Critical |
| TS-002 | Concurrent booking same slot | Integration | Critical |
| TS-003 | Availability calculation | Unit | High |

## 7. Architecture
### System Components
<!-- include: architecture/application.archimate#summary -->

### Data Models
| Table | Purpose | Key Fields |
|-------|---------|------------|
| appointments | Booking records | id, patient_id, provider_id, slot_time, status |
| provider_availability | Weekly schedules | provider_id, day_of_week, start_time, end_time |
| blocked_times | Exceptions | provider_id, start_datetime, end_datetime, reason |

### APIs
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/slots | GET | Search available slots |
| /api/v1/appointments | POST | Book appointment |
| /api/v1/appointments/{id} | DELETE | Cancel appointment |

## 8. Risks
<!-- include: risks.md -->

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| TR-001 | EHR API rate limits | Medium | High | Implement caching, queue writes |
| TR-002 | Concurrent booking conflicts | High | Medium | Optimistic locking, retry logic |
| DR-001 | Epic FHIR API changes | Low | High | Version pinning, adapter pattern |

## 9. Appendix
### References
- Epic FHIR R4 API Documentation
- HIPAA Security Rule Requirements

### Glossary
- **Slot**: A bookable time period with a specific provider
- **Visit Type**: Category of appointment (routine, follow-up, etc.)

### Open Questions
- [ ] How to handle same-day appointment requests?
- [ ] What's the cancellation policy window?
```

## Critical Requirements
1. **Dependency syntax**: MUST use `Depends on: [X, Y]` format - Task Master parses this
2. **Entry/Exit criteria**: Every phase needs both - enables automation
3. **Acceptance criteria**: Every task needs acceptance + test strategy
4. **Include markers**: Use `<!-- include: path -->` for files >500 tokens

## Anti-patterns (DO NOT)
- ❌ Missing dependencies: "Implement feature" without [depends on]
- ❌ Vague acceptance: "Works correctly" instead of specific criteria
- ❌ Inline large content: Embedding full OpenAPI spec instead of include
- ❌ Circular dependencies: A depends on B depends on A

## Output Location
`projects/{project}/docs/PRD.md`

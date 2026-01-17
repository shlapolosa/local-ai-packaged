[94m[1m| [0m[90m skill    [0mLoaded skill: test-strategy
Here's the code based on the provided specifications:

```python
import os, sys
from toolkit import toolkit_baseDir

# Tool Call Response: Test Strategy Example Output
output = """
# Test Strategy: Patient Appointment Portal

## 1. Test Pyramid


        /\
       /  \        E2E: 10% (5 tests)
      /----\       Critical user journeys
     /      \
    /--------\     Integration: 20% (15 tests)
   /          \    API endpoints, DB operations
  /------------\
 /              \  Unit: 70% (50 tests)
/________________\ Services, validators, utilities

### Distribution
| Layer | Count | Coverage Target | Run Time |
|-------|-------|-----------------|----------|
| Unit | 50 | 80% line, 70% branch | <30s |
| Integration | 15 | All endpoints | <2min |
| E2E | 5 | Critical paths | <5min |

## 2. Coverage Requirements

| Component | Line | Branch | Function | Rationale |
|-----------|------|--------|----------|-----------|
| scheduling.service.ts | 90% | 85% | 100% | Core business logic |
| availability.service.ts | 90% | 85% | 100% | Critical calculations |
| *.controller.ts | 80% | 70% | 95% | Request handling |
| *.repository.ts | 75% | 65% | 90% | Data access |
| utils/*.ts | 85% | 75% | 95% | Shared utilities |

## 3. Test Categories

### 3.1 Functional Tests
| Category | Focus | Tools |
|----------|-------|-------|
| Unit | Pure functions, business logic | Jest/Vitest |
| API | Endpoint contracts, validation | Supertest |
| Database | Queries, transactions, constraints | Testcontainers |

### 3.2 Non-Functional Tests
| Category | Requirement | Tool |
|----------|-------------|------|
| Performance | p95 < 200ms | k6, Artillery |
| Security | OWASP Top 10 | OWASP ZAP |
| Accessibility | WCAG 2.1 AA | axe-core |
| Load | 100 concurrent users | k6 |

## 4. Test Environments

| Environment | Purpose | Data Strategy |
|-------------|---------|---------------|
| Local | Development | SQLite + fixtures |
| CI | Automated tests | Testcontainers + seeded |
| Staging | Integration | Anonymized production |

## 5. Quality Gates

### PR Merge Requirements
- [ ] All unit tests pass
- [ ] Coverage >= thresholds
- [ ] No new security vulnerabilities
- [ ] API contract tests pass

### Release Requirements
- [ ] All integration tests pass
- [ ] E2E critical path tests pass
- [ ] Performance benchmarks met
- [ ] Security scan clean

## 6. Test Data Strategy

### Fixtures
```python
# fixtures/appointments.ts
export const validAppointment = {
  patientId: 'patient-123',
  providerId: 'provider-456',
  scheduledStart: '2024-01-15T09:00:00Z',
  visitType: 'routine'
};

export const conflictingAppointment = {
  ...validAppointment,
  scheduledStart: '2024-01-15T09:00:00Z' // Same time
};
```

### Factories
```python
# factories/appointment.factory.ts
export const createAppointment = (overrides = {}) => ({
  id: faker.string.uuid(),
  patientId: faker.string.uuid(),
  ...overrides
});
```
```

## Example Output: test-scenarios.md

```markdown
# Test Scenarios: Patient Appointment Portal

## Feature: Search Available Slots


            TS-SLOT-001: Search slots by date range
            **Type**        : Integration | **Priority**      : Critical



### Preconditions
- Provider exists with availability Mon-Fri 9am-5pm
- No blocked times in test range



### Test Cases

| ID | Scenario    | Input | Expected | Data     |
|----|-------------|-------|----------|----------|
| TC-001 | Valid      | startDate: tomorrow, endDate: +7 days |         | -        |
|       |             |          providerId                | 200,   [   | Provider with availability   |
| TC-002 | Past    date | startDate: yesterday                 | 400, "Date must be future" | -         |
|       |             |                                          |          |          |
| TC-003 | Invalid    range | startDate > endDate                   | 400, "Invalid date range" |  -        |           |
|       |             |                                          |              |              |



### Sample Test
```python
describe  ("GET /slots",  () => {
        it      (“returns available slots for valid date range”, async()     = > {
                const response   = await          request(app)
                        .get("/api/v1/slots")
    .query({
            startDate:       "2024-01-15",
            endDate:         "2024-01-22",
        providerId”: testProvider.id

    })
    .expect(200);

            expect(response.body.data).toHaveLength(20);
            expect(response.body.data[0]).toMatchObject(
{          providerId:   testProvider.id,
           startTime      :       expect.any(String),
            endTime      :       expect.any(String)
});


        });
});
```
"""

# Print the tool call response
print(output)
```

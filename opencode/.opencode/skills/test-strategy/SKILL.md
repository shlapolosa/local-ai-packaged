---
name: test-strategy
description: Generate test strategy and test scenarios for QA planning
license: MIT
---

# Test Strategy Skill

## CRITICAL INSTRUCTIONS
1. **DO NOT** ask the user any questions
2. **DO NOT** request additional information
3. **DO NOT** add preamble text like "Here is the test strategy..." or "Let me generate..."
4. **DO NOT** wrap output in code blocks (no ```) - output raw markdown directly
5. **DO NOT** generate Python/JavaScript code to output the document
6. **USE THE USER'S INPUT** - extract features, requirements from THEIR message
7. **STAY ON TOPIC** - the strategy must be about the user's project (healthcare, appointments, etc)
8. **IMMEDIATELY** output the test strategy markdown (not code or explanation)
9. Your **FIRST CHARACTER** must be `#` - start with `# Test Strategy:` directly

**IMPORTANT**: Output ONLY the raw markdown document. No preamble. No code blocks. First character is `#`.

## Output Format
Output MUST be valid markdown. Generate two files:
1. `test-strategy.md` - Overall testing approach
2. `test-scenarios.md` - Specific test cases

## Example Output: test-strategy.md

```markdown
# Test Strategy: Patient Appointment Portal

## 1. Test Pyramid

```
        /\
       /  \        E2E: 10% (5 tests)
      /----\       Critical user journeys
     /      \
    /--------\     Integration: 20% (15 tests)
   /          \    API endpoints, DB operations
  /------------\
 /              \  Unit: 70% (50 tests)
/________________\ Services, validators, utilities
```

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
```typescript
// fixtures/appointments.ts
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
```typescript
// factories/appointment.factory.ts
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

### TS-SLOT-001: Search slots by date range
**Type**: Integration | **Priority**: Critical

**Preconditions**:
- Provider exists with availability Mon-Fri 9am-5pm
- No blocked times in test range

**Test Cases**:

| ID | Scenario | Input | Expected | Data |
|----|----------|-------|----------|------|
| TC-001 | Valid date range | startDate: tomorrow, endDate: +7 days | 200, slots array | Provider with availability |
| TC-002 | Past date | startDate: yesterday | 400, "Date must be future" | - |
| TC-003 | Invalid range | startDate > endDate | 400, "Invalid date range" | - |
| TC-004 | No availability | Date with no providers | 200, empty array | No availability records |

**Sample Test**:
```typescript
describe('GET /slots', () => {
  it('returns available slots for valid date range', async () => {
    const response = await request(app)
      .get('/api/v1/slots')
      .query({
        startDate: '2024-01-15',
        endDate: '2024-01-22',
        providerId: testProvider.id
      })
      .expect(200);

    expect(response.body.data).toHaveLength(20);
    expect(response.body.data[0]).toMatchObject({
      providerId: testProvider.id,
      startTime: expect.any(String),
      endTime: expect.any(String)
    });
  });
});
```

---

## Feature: Book Appointment

### TS-BOOK-001: Successfully book available slot
**Type**: Integration | **Priority**: Critical

**Preconditions**:
- Available slot exists
- Patient authenticated

**Test Cases**:

| ID | Scenario | Input | Expected |
|----|----------|-------|----------|
| TC-010 | Valid booking | Valid slotId, patientId | 201, confirmation number |
| TC-011 | Slot taken | Already booked slotId | 409, "Slot unavailable" |
| TC-012 | Invalid slot | Non-existent slotId | 404, "Slot not found" |
| TC-013 | Missing patient | No patientId | 400, validation error |

**Edge Cases**:
- Concurrent booking of same slot (race condition)
- Booking at exact slot boundary time
- Patient already has appointment at same time

**Sample Test**:
```typescript
describe('POST /appointments', () => {
  it('creates appointment and returns confirmation', async () => {
    const response = await request(app)
      .post('/api/v1/appointments')
      .send({
        slotId: availableSlot.id,
        patientId: 'patient-123',
        reasonForVisit: 'Annual checkup'
      })
      .expect(201);

    expect(response.body).toMatchObject({
      confirmationNumber: expect.stringMatching(/^APT-[A-Z0-9]{8}$/),
      status: 'confirmed'
    });
  });

  it('handles concurrent booking with optimistic locking', async () => {
    const [result1, result2] = await Promise.all([
      request(app).post('/api/v1/appointments').send({ slotId: slot.id, patientId: 'p1' }),
      request(app).post('/api/v1/appointments').send({ slotId: slot.id, patientId: 'p2' })
    ]);

    const successes = [result1, result2].filter(r => r.status === 201);
    const conflicts = [result1, result2].filter(r => r.status === 409);

    expect(successes).toHaveLength(1);
    expect(conflicts).toHaveLength(1);
  });
});
```

---

## Feature: Cancel Appointment

### TS-CANCEL-001: Cancel within allowed window
**Type**: Integration | **Priority**: High

**Test Cases**:

| ID | Scenario | Input | Expected |
|----|----------|-------|----------|
| TC-020 | Valid cancel | appointmentId, >24h before | 204 |
| TC-021 | Too late | appointmentId, <24h before | 409, "Cannot cancel" |
| TC-022 | Already cancelled | Cancelled appointmentId | 409, "Already cancelled" |
| TC-023 | Not found | Invalid appointmentId | 404 |

---

## E2E Scenarios

### E2E-001: Complete Booking Flow
**Type**: E2E | **Priority**: Critical

**Steps**:
1. Patient logs in
2. Searches for available slots
3. Selects a slot
4. Confirms booking
5. Receives confirmation email
6. Views appointment in "My Appointments"

**Assertions**:
- Appointment visible in list
- Confirmation email received
- Slot no longer available
```

## Checklist
- ✅ Test pyramid ratios defined (70/20/10)
- ✅ Coverage targets per component type
- ✅ Sample test code included
- ✅ Edge cases identified
- ✅ Test data strategy defined
- ✅ Quality gates specified

## Anti-patterns (DO NOT)
- ❌ No specific scenarios: "Test the booking feature"
- ❌ Missing edge cases: Only happy path tests
- ❌ No test data: Tests without fixtures/factories
- ❌ Vague assertions: "Response should be correct"

## Output Locations
- `projects/{project}/docs/test-strategy.md`
- `projects/{project}/docs/test-scenarios.md`

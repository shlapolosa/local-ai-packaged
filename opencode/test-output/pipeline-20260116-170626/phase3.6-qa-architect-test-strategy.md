[94m[1m| [0m[90m skill    [0mLoaded skill: test-strategy
# Test Strategy:

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

## Checklist
- ✅ Test pyramid ratios defined (70/20/10)
- ✅ Coverage targets per component type
- ✅ Sample test code included
- ✅ Edge cases identified
- ✅ Test data strategy defined
- ✅ Quality gates specified

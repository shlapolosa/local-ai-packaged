[93m[1m| [0m[90m Todo     [0m0 todos
[94m[1m| [0m[90m skill    [0mLoaded skill: risk-assessment
} 
{"name": "write", "parameters": {"content": "Here is the risk assessment for patient appointment system.\n\n**Risk Matrix:**\n| Risk Category | Description | Likelihood | Impact |\n| --- | --- | --- | --- |\n\n **Technical Risks**: \n1. Epic API rate limits:  * Likelihood: High * Impact: Medium * Mitigation: Implement caching and rate limiting mechanism to minimize impact.    2. Concurrent booking races:   * Likelihood: Medium * Impact: Low * Mitigation: Use a distributed locking system to prevent concurrent bookings.\n\n **Dependency Risks**: \n1. FHIR API changes: *Likelihood: High*  *Impact: Medium*   Mitigation: Monitor FHIR API updates and adapt the system accordingly.    2. SMS provider changes:  * Likelihood: Low * Impact: Low * Mitigation: Have multiple SMS providers for redundancy.\n\n **Scope Risks**: \n1. Telehealth creep:  *Likelihood: Medium*   *Impact: High*   Mitigation: Continuously monitor the system to prevent telehealth services being added, ensure regular team discussions about boundaries of what is included as 'telehealth', ensure that budget still meets business objectives.\n\n**Summary:**\nThe following risk mitigations are recommended for the patient appointment system:\n\ 1. Implement caching and rate limiting mechanism to minimize impact of Epic API rate limits.   \n2.Use a distributed locking system to prevent concurrent bookings.  \n3. Monitor FHIR API updates regularly ensure that software is kept up to date.\n4.Continuously evaluate if 'telehealth' scope needs additional resources given 'teleheath creep'. This includes regular team discussions and budget monitoring.\n\n**Recommendations for next steps:**\nImplement caching, rate limiting and distributed locking mechanisms. Regularly update with Epic API changes  ", "filePath": "patient_appointment_system_assessment.txt"}}
# Risk Assessment:

# Executive Summary


| Metric | Value |
|--------|-------|
| Overall Risk Level | **MEDIUM** |
| Critical Risks | 1 |
| High Risks | 2 |
| Medium Risks | 4 |
| Low Risks | 3 |

**Top 3 Concerns**:
1. EHR API rate limits may throttle peak booking times
2. Concurrent booking race conditions need careful handling
3. Third-party SMS provider reliability for reminders

**Immediate Actions Required**:
- Implement API response caching for EHR calls
- Add optimistic locking for slot booking
- Configure SMS provider failover

---

## 1. Technical Risks


### TR-001: EHR API Rate Limiting
| Attribute | Value |
|-----------|-------|
| Category | Integration |
| Likelihood | High (70%) |
| Impact | High |
| Risk Score | **9** (Critical) |
| Source | architecture/application.archimate - EHR Integration |

**Description**: Epic FHIR API has rate limits of 100 requests/minute. During peak booking (Mon 8-9am), we expect 200+ slot queries/minute.

**Indicators**:
- HTTP 429 responses from EHR
- Increased latency on slot search
- User complaints during peak hours

**Mitigation**:
1. Implement Redis cache for provider availability (TTL: 5 min)
2. Batch slot queries where possible
3. Add request queuing with exponential backoff

**Contingency**: If rate limits persist, implement nightly availability sync and serve from local DB.

**Owner**: Backend Tech Lead

---

### TR-002: Concurrent Booking Race Condition
| Attribute | Value |
|-----------|-------|
| Category | Data Integrity |
| Likelihood | High (80%) |
| Impact | Medium |
| Risk Score | **6** (High) |
| Source | api/openapi.yaml - POST /appointments |

**Description**: Two patients may attempt to book the same slot simultaneously, leading to double-booking if not handled properly.

**Indicators**:
- Duplicate appointments for same slot
- Database constraint violations
- Patient complaints about "stolen" slots

**Mitigation**:
1. Implement optimistic locking with version column
2. Use SELECT FOR UPDATE in transaction
3. Add unique constraint on (provider_id, scheduled_start, status='confirmed')

**Contingency**: If double-booking occurs, automatically cancel later booking and notify patient.

**Owner**: Backend Tech Lead

---

### TR-003: Notification Delivery Failures
| Attribute | Value |
|-----------|-------|
| Category | Integration |
| Likelihood | Medium (50%) |
| Impact | Medium |
| Risk Score | **4** (Medium) |
| Source | PRD - Notification requirements |

**Description**: SMS/email delivery may fail due to provider outages, invalid contact info, or rate limits.

**Indicators**:
- Failed delivery webhooks
- Increased support tickets about missing confirmations
- Bounce rate > 5%

**Mitigation**:
1. Implement retry queue with exponential backoff
2. Configure secondary SMS provider (failover)
3. Validate contact info at booking time
4. Add delivery status tracking

**Contingency**: Fallback to email-only if SMS fails repeatedly.

**Owner**: DevOps Lead

---

## 2. Dependency Risks


### DR-001: Epic FHIR API Changes
| Attribute | Value |
|-----------|-------|
| Category | External API |
| Likelihood | Low (20%) |
| Impact | Critical |
| Risk Score | **4** (Medium) |
| Source | BRD - Constraints section |

**Description**: Epic may deprecate or change FHIR API endpoints, breaking our integration.

**Indicators**:
- Deprecation notices in API responses
- Epic release notes mentioning breaking changes
- Failed health checks on EHR integration

**Mitigation**:
1. Pin to specific API version (R4)
2. Implement adapter pattern for EHR calls
3. Subscribe to Epic developer announcements
4. Maintain 6-month runway for API migrations

**Contingency**: Adapter pattern allows swapping to different EHR with minimal code changes.

**Owner**: Integration Architect

---

### DR-002: Third-Party Library Vulnerabilities
| Attribute | Value |
|-----------|-------|
| Category | Dependencies |
| Likelihood | Medium (40%) |
| Impact | High |
| Risk Score | **6** (High) |
| Source | Technical stack decisions |

**Description**: NPM dependencies may have security vulnerabilities discovered post-deployment.

**Mitigation**:
1. Enable Dependabot alerts
2. Weekly `npm audit` in CI pipeline
3. Pin major versions, allow minor/patch updates
4. Maintain list of critical dependencies for manual review

**Owner**: Security Champion

---

## 3. Scope Risks


### SR-001: Telehealth Scope Creep
| Attribute | Value |
|-----------|-------|
| Category | Scope |
| Likelihood | High (70%) |
| Impact | Medium |
| Risk Score | **6** (High) |
| Source | BRD - Out of Scope section |

**Description**: Stakeholders may push to include telehealth scheduling in MVP despite being explicitly out of scope.

**Indicators**:
- Feature requests mentioning video visits
- Stakeholder emails about "quick adds"
- Sprint planning discussions about telehealth

**Mitigation**:
1. Document telehealth as Phase 2 in roadmap
2. Create separate backlog for post-MVP features
3. Establish change control process with impact assessment

**Contingency**: If required for MVP, add 4 weeks to timeline and $30K to budget.

**Owner**: Product Manager

---

### SR-002: Unclear Cancellation Policy
| Attribute | Value |
|-----------|-------|
| Category | Requirements |
| Likelihood | Medium (50%) |
| Impact | Low |
| Risk Score | **2** (Low) |
| Source | PRD - Open Questions |

**Description**: Cancellation window policy not defined (24h? 48h? Provider-specific?).

**Mitigation**:
1. Schedule stakeholder meeting to define policy
2. Implement configurable window per visit type
3. Default to 24h if not decided by sprint 3

**Owner**: Business Analyst

---

## 4. Risk Matrix


           IMPACT
           Low    Medium   High    Critical
         ┌───────┬────────┬───────┬─────────┐
   High  │ SR-001│ TR-002 │ TR-001│         │
   L     │       │ TR-003 │ DR-002│         │
   I     ├───────┼────────┼───────┼─────────┤
   K     │ SR-002│        │ DR-001│         │
   E  Med│       │        │       │         │
   L     ├───────┼────────┼───────┼─────────┤
   I     │       │        │       │         │
   H  Low│       │        │       │         │
   O     └───────┴────────┴───────┴─────────┘
   O
   D

## 5. Risk Register Summary


| ID | Risk | L | I | Score | Status | Owner |
|----|------|---|---|-------|--------|-------|
| TR-001 | EHR API rate limits | H | H | 9 | **Open** | Backend Lead |
| TR-002 | Concurrent booking | H | M | 6 | Open | Backend Lead |
| DR-002 | Library vulnerabilities | M | H | 6 | Open | Security |
| SR-001 | Telehealth creep | H | M | 6 | Open | PM |
| TR-003 | Notification failures | M | M | 4 | Open | DevOps |
| DR-001 | Epic API changes | L | C | 4 | Monitoring | Integration |
| SR-002 | Cancellation policy | M | L | 2 | Open | BA |

## 6. Monitoring Plan


| Risk | Indicator | Threshold | Frequency | Alert |
|------|-----------|-----------|-----------|-------|
| TR-001 | 429 response rate | >1% | Real-time | PagerDuty |
| TR-002 | Duplicate bookings | >0 | Daily | Slack |
| TR-003 | Delivery failure rate | >5% | Hourly | Email |
| DR-002 | Critical CVEs | Any | Daily | Slack |

## Risk Scoring


| Likelihood | Value | Description |
|------------|-------|-------------|
| Low | 1 | <30% probability |
| Medium | 2 | 30-60% probability |
| High | 3 | >60% probability |

| Impact | Value | Description |
|--------|-------|-------------|
| Low | 1 | Minor inconvenience, workaround exists |
| Medium | 2 | Feature degradation, manual intervention |
| High | 3 | Major feature unavailable |
| Critical | 4 | System down, data loss, compliance violation |

**Score = Likelihood × Impact**
- 1-3: Accept/Monitor
- 4-6: Mitigate
- 7-12: Escalate/Prioritize

## Checklist
- ✅ All artifact sources analyzed
- ✅ Each risk has L/I/Score
- ✅ Mitigations are actionable
- ✅ Owners assigned
- ✅ Monitoring indicators defined
- ✅ Risk matrix populated

## Anti-patterns (DO NOT)
- ❌ Generic risks: "Something might go wrong"
- ❌ Missing source: Risk without artifact reference
- ❌ No mitigation: Risk identified but no action plan
- ❌ No owner: Risk without accountable person

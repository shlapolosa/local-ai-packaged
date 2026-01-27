# E2E Pipeline Test - Full Workflow Validation

## Test Overview

This test validates the complete pipeline flow from Business Analysis through Software Delivery using:
- **Frontend**: Open WebUI (chrome-devtools MCP)
- **Backend**: n8n workflow monitoring (n8n-mcp)
- **Manual Gates**: GitHub PR approvals

## Pipeline Flow Under Test

```
Business Analysis (BRD) → Architecture → Solution Architecture
                                              ↓
                                    ┌─────────┴─────────┐
                                    ↓                   ↓
                              Test Strategy      Risk Assessment
                                    └─────────┬─────────┘
                                              ↓
                                    Project Management (PRD)
                                              ↓
                                    Software Delivery (Deploy)
```

---

## Test Project Definition

### Project Name
`healthcare-appointment-scheduler`

### Project Brief
```
Create a healthcare appointment scheduling system for a multi-location medical clinic network.

The system should allow:
- Patients to book, reschedule, and cancel appointments online
- Doctors to manage their availability and view schedules
- Clinic administrators to oversee all locations and generate reports
- Integration with existing EHR (Electronic Health Records) systems
- SMS and email appointment reminders
- Telemedicine video consultation support

Key Requirements:
- HIPAA compliance for patient data protection
- Support for 50+ clinic locations
- Mobile-responsive web application
- Real-time availability updates
- Multi-language support (English, Spanish, Mandarin)
- Accessibility compliance (WCAG 2.1 AA)

Technical Constraints:
- Must integrate with Epic EHR via FHIR APIs
- Cloud-native deployment on Kubernetes
- 99.9% uptime SLA requirement
- Support 10,000 concurrent users
```

---

## Test Execution Steps

### Stage 1: Business Analysis Pipeline (BRD Generation)

**Trigger Method**: Open WebUI Chat with Business_Analyst_v2

**Input Prompt**:
```
Create a BRD for a project called healthcare-appointment-scheduler - a healthcare appointment scheduling system for a multi-location medical clinic network that allows patients to book appointments online, doctors to manage availability, and administrators to oversee operations. Key requirements include HIPAA compliance, Epic EHR integration via FHIR, telemedicine support, and 99.9% uptime SLA.
```

**Expected Response**: Async acknowledgment with job ID

**Monitoring**:
- Check n8n execution for Business Analysis Pipeline (nmqyIEwcwVfiIIOu)
- Verify BRD artifact created in database
- Confirm GitHub branch created: `healthcare-appointment-scheduler`

**Success Criteria**:
- [ ] Execution completes without errors
- [ ] BRD markdown generated
- [ ] GitHub PR created for BRD
- [ ] Azure DevOps branch created

---

### Stage 2: Architecture Pipeline (ArchiMate)

**Trigger Method**: Open WebUI Chat with Architecture_Agent

**Input Prompt**:
```
Generate architecture artifacts for project healthcare-appointment-scheduler based on the completed BRD.
```

**Expected Response**: Async acknowledgment

**Monitoring**:
- Check n8n execution for Architecture Pipeline (R4SsOqGqQIkRwUPT)
- Verify ArchiMate diagrams generated

**Success Criteria**:
- [ ] Business architecture artifacts created
- [ ] Data architecture artifacts created
- [ ] Application architecture artifacts created
- [ ] Infrastructure architecture artifacts created
- [ ] Security architecture artifacts created
- [ ] GitHub PR created for architecture artifacts

---

### Stage 3: Solution Architecture Pipeline (OAM/OpenAPI)

**Trigger Method**: Open WebUI Chat with Solution_Architect_v2

**Input Prompt**:
```
Generate solution architecture for project healthcare-appointment-scheduler including OpenAPI specs and OAM definitions.
```

**Expected Response**: Async acknowledgment

**Monitoring**:
- Check n8n execution for Solution Architecture Pipeline (smxRuLpxe8181lbw)

**Success Criteria**:
- [ ] OpenAPI specification generated
- [ ] OAM component definitions created
- [ ] SQL schema generated (if applicable)
- [ ] GitHub PR created for solution artifacts

---

### Stage 4a: Test Strategy Pipeline

**Trigger Method**: Open WebUI Chat with QA_Architect

**Input Prompt**:
```
Generate test strategy for project healthcare-appointment-scheduler based on the architecture and solution artifacts.
```

**Expected Response**: Async acknowledgment

**Monitoring**:
- Check n8n execution for Test Strategy Pipeline (DZdCDfvObweaHen4)

**Success Criteria**:
- [ ] Test strategy document generated
- [ ] Test cases defined
- [ ] GitHub PR created for test artifacts

---

### Stage 4b: Risk Assessment Pipeline (Parallel with 4a)

**Trigger Method**: Open WebUI Chat with Risk_Analyst

**Input Prompt**:
```
Perform risk assessment for project healthcare-appointment-scheduler based on the architecture and compliance requirements.
```

**Expected Response**: Async acknowledgment

**Monitoring**:
- Check n8n execution for Risk Assessment Pipeline (FUDBTPAjmDnFlg7h)

**Success Criteria**:
- [ ] Risk register created
- [ ] HIPAA compliance checklist generated
- [ ] Mitigation strategies defined
- [ ] GitHub PR created for risk artifacts

---

### Stage 5: Project Management Pipeline (PRD)

**Trigger Method**: Open WebUI Chat with PM_Agent

**Input Prompt**:
```
Generate the final PRD for project healthcare-appointment-scheduler consolidating all architecture, test, and risk artifacts.
```

**Expected Response**: Async acknowledgment

**Monitoring**:
- Check n8n execution for Project Management Pipeline (VvpkyZ9c4dCNv4rd)

**Success Criteria**:
- [ ] Final PRD document generated
- [ ] All artifacts consolidated
- [ ] GitHub PR created for PRD

---

### Stage 6: Software Delivery Pipeline

**Trigger Method**: Open WebUI Chat with DevOps_Agent

**Input Prompt**:
```
Generate deployment artifacts for project healthcare-appointment-scheduler including CI/CD pipelines and infrastructure definitions.
```

**Expected Response**: Async acknowledgment

**Monitoring**:
- Check n8n execution for Software Delivery Pipeline (FlqPvbx2ICZvJiQr)

**Success Criteria**:
- [ ] CI/CD pipeline definitions created
- [ ] Kubernetes manifests generated
- [ ] Infrastructure-as-code templates created
- [ ] GitHub PR created for delivery artifacts
- [ ] All PRs merged to main branch

---

## Workflow IDs Reference

| Pipeline | Workflow ID | Webhook |
|----------|-------------|---------|
| Business Analysis | nmqyIEwcwVfiIIOu | /webhook/business-analysis |
| Architecture | R4SsOqGqQIkRwUPT | /webhook/architecture |
| Solution Architecture | smxRuLpxe8181lbw | /webhook/solution-architecture |
| Test Strategy | DZdCDfvObweaHen4 | /webhook/test-strategy |
| Risk Assessment | FUDBTPAjmDnFlg7h | /webhook/risk-assessment |
| Project Management | VvpkyZ9c4dCNv4rd | /webhook/project-management |
| Software Delivery | FlqPvbx2ICZvJiQr | /webhook/software-delivery |

---

## MCP Commands Reference

### Chrome DevTools MCP
```bash
# Navigate to Open WebUI
mcp-cli call chrome-devtools/navigate_page '{"url": "https://openwebui.socrates-hlapolosa.org"}'

# Take snapshot to see current state
mcp-cli call chrome-devtools/take_snapshot '{}'

# Click on New Chat
mcp-cli call chrome-devtools/click '{"uid": "<uid>"}'

# Fill prompt
mcp-cli call chrome-devtools/fill '{"uid": "<uid>", "value": "<prompt>"}'

# Submit with Enter
mcp-cli call chrome-devtools/press_key '{"key": "Enter"}'
```

### N8N MCP
```bash
# List recent executions
mcp-cli call n8n-mcp/n8n_executions '{"action": "list", "workflowId": "<id>", "limit": 5}'

# Get execution details
mcp-cli call n8n-mcp/n8n_executions '{"action": "get", "id": "<execution_id>", "mode": "summary"}'

# Check workflow health
mcp-cli call n8n-mcp/n8n_health_check '{}'
```

---

## Test Execution Script

To run this test, execute the following stages in order. Each stage follows a handoff pattern between Claude (automation) and User (manual merge).

### Execution Flow Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│  CLAUDE: Submit prompt → Monitor execution → Confirm complete   │
│                              ↓                                  │
│  USER: "merged" → (merge PR in GitHub)                         │
│                              ↓                                  │
│  CLAUDE: Proceed to next stage automatically                    │
└─────────────────────────────────────────────────────────────────┘
```

### User Commands

| Command | Action |
|---------|--------|
| `merged` | Signal that PR has been merged, proceed to next stage |
| `skip` | Skip current stage and proceed to next |
| `status` | Show current test status |
| `pause` | Pause test execution |
| `resume` | Resume test execution |

### Automated Test Sequence

```
1. Login to Open WebUI (if needed)
2. Stage 1: Business Analysis
   - CLAUDE: Submit BRD prompt, monitor execution, confirm complete
   - USER: Type "merged" after merging PR in GitHub
   - CLAUDE: Proceed to Stage 2
3. Stage 2: Architecture
   - CLAUDE: Submit architecture prompt, monitor execution
   - USER: Type "merged" after merging PR
   - CLAUDE: Proceed to Stage 3
4. Stage 3: Solution Architecture
   - CLAUDE: Submit solution architecture prompt, monitor execution
   - USER: Type "merged" after merging PR
   - CLAUDE: Proceed to Stages 4a & 4b
5. Stages 4a & 4b (parallel): Test Strategy + Risk Assessment
   - CLAUDE: Submit both prompts, monitor both executions
   - USER: Type "merged" after merging BOTH PRs
   - CLAUDE: Proceed to Stage 5
6. Stage 5: Project Management
   - CLAUDE: Submit PRD prompt, monitor execution
   - USER: Type "merged" after merging PR
   - CLAUDE: Proceed to Stage 6
7. Stage 6: Software Delivery
   - CLAUDE: Submit deployment prompt, monitor execution
   - USER: Type "merged" after merging final PR
8. CLAUDE: Verify all artifacts and report final status
```

### GitHub Repository

**Repo URL**: https://github.com/shlapolosa/software-delivery
**Project Folder**: `healthcare-appointment-scheduler/`

---

## Expected Final Outputs

After successful completion, the GitHub repository should contain:

```
healthcare-appointment-scheduler-docs/
├── docs/
│   ├── BRD.md                    # Business Requirements Document
│   ├── architecture/
│   │   ├── business-architecture.md
│   │   ├── data-architecture.md
│   │   ├── application-architecture.md
│   │   ├── infrastructure-architecture.md
│   │   └── security-architecture.md
│   ├── solution/
│   │   ├── openapi-spec.yaml
│   │   ├── oam-definitions.yaml
│   │   └── sql-schema.sql
│   ├── quality/
│   │   ├── test-strategy.md
│   │   └── risk-assessment.md
│   ├── PRD.md                    # Final Product Requirements Document
│   └── delivery/
│       ├── ci-cd-pipeline.yaml
│       ├── kubernetes-manifests/
│       └── infrastructure/
```

---

## Test Status Tracking

| Stage | Status | Execution ID | Duration | PR Link |
|-------|--------|--------------|----------|---------|
| Business Analysis | ⏸️ Waiting PR | 1321690 | ~2 min | [Check PR](https://github.com/shlapolosa/software-delivery/pulls) |
| Architecture | ⏳ Pending | - | - | - |
| Solution Architecture | ⏳ Pending | - | - | - |
| Test Strategy | ⏳ Pending | - | - | - |
| Risk Assessment | ⏳ Pending | - | - | - |
| Project Management | ⏳ Pending | - | - | - |
| Software Delivery | ⏳ Pending | - | - | - |

**Legend**: ⏳ Pending | 🔄 Running | ✅ Passed | ❌ Failed | ⏸️ Waiting PR

**Current Stage**: Business Analysis - Waiting for user to merge PR

---

## Notes

- Each stage requires the previous stage's PR to be approved before proceeding
- Test Strategy and Risk Assessment can run in parallel (Stage 4a/4b)
- Monitor n8n execution logs for any errors
- Check Azure DevOps for mirrored artifacts
- All timestamps are in UTC

**Test Created**: 2026-01-27
**Test Version**: 1.0

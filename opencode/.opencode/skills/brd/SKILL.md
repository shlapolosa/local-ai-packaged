---
name: brd
description: Generate Business Requirements Document as JSON (transformed to Markdown via script)
license: MIT
---

# BRD Generation Skill

You are outputting a Business Requirements Document as **JSON**. Your entire response is a single JSON object.

## CRITICAL INSTRUCTIONS

1. **OUTPUT ONLY JSON** - No explanations, no markdown, no code blocks
2. **FIRST CHARACTER MUST BE `{`** - Start immediately with the JSON object
3. **VALID JSON REQUIRED** - Must be parseable by `json.loads()`
4. **NO TRAILING TEXT** - End with `}` and nothing else
5. **USE THE USER'S INPUT** - Extract project details from their problem statement
6. **STAY ON TOPIC** - The BRD must be about the user's specific project

## JSON Schema

```json
{
  "type": "brd",
  "title": "Business Requirements Document: {Project Name}",
  "version": "1.0.0",
  "date": "YYYY-MM-DD",
  "executiveSummary": "Brief 2-3 sentence overview",
  "problemStatement": {
    "currentState": "Description of current situation",
    "painPoints": ["Pain point 1", "Pain point 2"],
    "impact": "Quantified business impact"
  },
  "businessObjectives": [
    {"id": "O1", "description": "Objective description", "metric": "Measurable KPI"}
  ],
  "stakeholders": [
    {"role": "Role name", "responsibilities": "Key responsibilities", "concerns": "Main concerns"}
  ],
  "scope": {
    "inScope": ["Capability 1", "Capability 2"],
    "outOfScope": ["Excluded item 1"]
  },
  "constraints": ["Constraint 1", "Constraint 2"],
  "assumptions": ["Assumption 1", "Assumption 2"],
  "successCriteria": ["Quantifiable metric 1", "Quantifiable metric 2"]
}
```

## Field Requirements

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | Always "brd" |
| `title` | Yes | Document title with project name |
| `executiveSummary` | Yes | 2-3 sentence overview |
| `problemStatement` | Yes | Current state, pain points, impact |
| `businessObjectives` | Yes | At least 3 objectives with metrics |
| `stakeholders` | Yes | At least 4 stakeholder roles |
| `scope.inScope` | Yes | At least 3 in-scope items |
| `scope.outOfScope` | Yes | At least 2 out-of-scope items |
| `constraints` | Yes | Technical, budget, timeline constraints |
| `assumptions` | Yes | Key dependencies |
| `successCriteria` | Yes | Measurable success metrics |

## Example Output

For a healthcare appointment booking system:

```json
{
  "type": "brd",
  "title": "Business Requirements Document: Healthcare Appointment Booking System",
  "version": "1.0.0",
  "date": "2024-01-15",
  "executiveSummary": "Enable patients to self-schedule appointments online, reducing call center volume by 40% and improving patient satisfaction scores. This addresses the current 8-minute average call time and 35% abandonment rate for phone-based scheduling.",
  "problemStatement": {
    "currentState": "Currently, 85% of appointments are booked via phone calls requiring 8-minute average call time. The call center handles 2,400 calls per day with 35% abandonment during peak hours.",
    "painPoints": [
      "High call volume overwhelms administrative staff during peak hours",
      "Patients cannot book appointments outside business hours (8am-5pm)",
      "No visibility into provider availability without calling",
      "Manual scheduling leads to double-bookings and data entry errors",
      "12-minute average hold time frustrates patients"
    ],
    "impact": "The clinic loses approximately 2,500 potential appointments per month due to phone system limitations. Patient satisfaction NPS has dropped to 32, and staff turnover in scheduling is 45% annually due to call volume stress."
  },
  "businessObjectives": [
    {"id": "O1", "description": "Reduce phone call volume for scheduling", "metric": "40% reduction in scheduling calls within 6 months"},
    {"id": "O2", "description": "Improve patient access to scheduling", "metric": "24/7 booking availability with <2 min average booking time"},
    {"id": "O3", "description": "Reduce appointment no-shows", "metric": "25% reduction via automated reminders"},
    {"id": "O4", "description": "Increase patient satisfaction", "metric": "NPS improvement from 32 to 50 within 12 months"}
  ],
  "stakeholders": [
    {"role": "Patients", "responsibilities": "Book and manage their appointments, receive reminders", "concerns": "Ease of use, privacy of health information, appointment availability"},
    {"role": "Clinic Schedulers", "responsibilities": "Handle complex scheduling, manage exceptions and overrides", "concerns": "Job security, workload changes, learning new system"},
    {"role": "Healthcare Providers", "responsibilities": "Set availability, manage schedule preferences", "concerns": "Schedule control, adequate buffer time between appointments"},
    {"role": "IT Department", "responsibilities": "System integration, security, maintenance", "concerns": "EHR integration complexity, HIPAA compliance, system reliability"},
    {"role": "Finance/Administration", "responsibilities": "ROI tracking, budget approval", "concerns": "Implementation cost, staff reallocation needs"}
  ],
  "scope": {
    "inScope": [
      "Patient self-scheduling for routine appointments",
      "Provider availability management dashboard",
      "Automated appointment reminders via SMS and email",
      "Integration with Epic EHR via FHIR R4 APIs",
      "Patient portal with appointment history",
      "Appointment cancellation and rescheduling",
      "Wait list management for cancelled slots"
    ],
    "outOfScope": [
      "Emergency or urgent care scheduling",
      "Procedure scheduling requiring pre-authorization",
      "Telehealth/video visit capabilities (Phase 2)",
      "Insurance eligibility verification",
      "Patient medical record access",
      "Prescription refill requests"
    ]
  },
  "constraints": [
    "Must integrate with Epic EHR via FHIR R4 APIs",
    "HIPAA compliance required for all PHI handling",
    "Budget limited to $250,000 for implementation",
    "Go-live required within 8 months",
    "Must support WCAG 2.1 AA accessibility standards",
    "Must support mobile devices (responsive design)"
  ],
  "assumptions": [
    "Epic FHIR APIs are available and well-documented",
    "Patients have email or mobile phone for receiving notifications",
    "Existing patient portal authentication can be extended",
    "Providers will maintain their availability calendars weekly",
    "SMS provider contract can support projected reminder volume"
  ],
  "successCriteria": [
    "40% reduction in scheduling phone calls within 6 months",
    "60% of appointments booked online within 6 months",
    "Zero HIPAA violations or security incidents",
    "95% system uptime during business hours",
    "Patient satisfaction score of 4.5/5 or higher for booking experience",
    "Less than 2 minutes average time to complete online booking"
  ]
}
```

## Guidelines

1. **Specific & Measurable** - Every objective needs a quantifiable metric
2. **Complete Stakeholders** - Include IT, finance, compliance - not just end users
3. **Clear Boundaries** - Explicit out-of-scope prevents scope creep
4. **Realistic Constraints** - Surface budget, timeline, regulatory requirements
5. **Business Language** - Avoid technical jargon; focus on outcomes

## Anti-patterns (DO NOT)

- ❌ Vague objectives: "Improve patient experience" (no metric)
- ❌ Missing stakeholders: Forgetting IT, compliance, finance
- ❌ Scope creep: Including "nice to have" features in scope
- ❌ Technical language: "Implement REST APIs" (save for PRD)
- ❌ Unmeasurable success: "Users will be happy"

## Post-Processing

The JSON output will be transformed to Markdown using:
```bash
python scripts/json-to-markdown.py input.json output.md
```

This produces a properly formatted BRD Markdown document.

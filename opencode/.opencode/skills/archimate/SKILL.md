---
name: archimate
description: Generate ArchiMate 3.1 models as JSON (transformed to XML via script)
license: MIT
---

# ArchiMate Modeling Skill

You are outputting an ArchiMate model as **JSON**. Your entire response is a single JSON object.

## CRITICAL INSTRUCTIONS

1. **OUTPUT ONLY JSON** - No explanations, no markdown, no code blocks
2. **FIRST CHARACTER MUST BE `{`** - Start immediately with the JSON object
3. **VALID JSON REQUIRED** - Must be parseable by `json.loads()`
4. **NO TRAILING TEXT** - End with `}` and nothing else

## JSON Schema

```json
{
  "name": "Model Name (e.g., Healthcare Appointment System - Business Layer)",
  "layer": "business|application|technology",
  "elements": [
    {
      "id": "unique-kebab-case-id",
      "type": "ArchiMate element type (see types below)",
      "name": "Display Name",
      "description": "What this element represents"
    }
  ],
  "relationships": [
    {
      "type": "Relationship type (see types below)",
      "source": "source-element-id",
      "target": "target-element-id"
    }
  ]
}
```

## Element Types by Layer

### Business Layer
| Type | Use For |
|------|---------|
| `BusinessActor` | Person or organization (Patient, Clinic, Vendor) |
| `BusinessRole` | Responsibility (Scheduler, Approver, Administrator) |
| `BusinessProcess` | Activity sequence (Book Appointment, Verify Insurance) |
| `BusinessService` | External capability (Scheduling Service, Notification Service) |
| `BusinessObject` | Information entity (Appointment, Patient Record, Invoice) |
| `BusinessFunction` | Internal capability (Scheduling, Billing, Reporting) |
| `BusinessEvent` | State change trigger (Appointment Requested, Payment Received) |

### Application Layer
| Type | Use For |
|------|---------|
| `ApplicationComponent` | Software module (Scheduling Module, Auth Service) |
| `ApplicationService` | App behavior (Slot Query, Booking API) |
| `ApplicationInterface` | Access point (REST API, GraphQL Endpoint) |
| `ApplicationFunction` | Internal app behavior (Validate Appointment) |
| `DataObject` | Structured data (AppointmentDTO, PatientRecord) |

### Technology Layer
| Type | Use For |
|------|---------|
| `Node` | Computing resource (Web Server, Database Server) |
| `Device` | Physical hardware (Load Balancer, Firewall) |
| `SystemSoftware` | OS/platform (PostgreSQL, Nginx, Docker) |
| `TechnologyService` | Infrastructure service (Storage, Compute, Network) |
| `Artifact` | Deployable (Docker Image, WAR file, Config file) |
| `CommunicationNetwork` | Network (VLAN, Internet, VPN) |

### Motivation Layer (for compliance/security)
| Type | Use For |
|------|---------|
| `Requirement` | Compliance need (HIPAA PHI Protection, Audit Logging) |
| `Constraint` | Limitation (Budget Limit, Timeline Constraint) |
| `Principle` | Guideline (Data Minimization, Least Privilege) |
| `Goal` | Target state (Reduce call volume 40%, HIPAA Compliance) |

## Relationship Types

| Type | Meaning | Direction |
|------|---------|-----------|
| `Serving` | Provides functionality to | Service → Consumer |
| `Realization` | Implements/realizes | Implementation → Abstraction |
| `Assignment` | Allocated to perform | Role → Process, Node → Artifact |
| `Access` | Reads/writes data | Process → DataObject |
| `Flow` | Transfer of data/control | Process → Process |
| `Composition` | Part of (strong) | Parent → Child |
| `Aggregation` | Contains (weak) | Container → Item |
| `Triggering` | Causes to start | Event → Process |
| `Association` | Generic relationship | Any → Any |

## Example Output

For a healthcare appointment booking system business layer:

```json
{
  "name": "Healthcare Appointment System - Business Layer",
  "layer": "business",
  "elements": [
    {"id": "patient", "type": "BusinessActor", "name": "Patient", "description": "Healthcare consumer seeking appointments"},
    {"id": "provider", "type": "BusinessActor", "name": "Healthcare Provider", "description": "Physician or medical staff"},
    {"id": "clinic-staff", "type": "BusinessActor", "name": "Clinic Staff", "description": "Administrative personnel"},
    {"id": "scheduler-role", "type": "BusinessRole", "name": "Appointment Scheduler", "description": "Role responsible for managing bookings"},
    {"id": "book-appointment", "type": "BusinessProcess", "name": "Book Appointment", "description": "Patient selects provider, date, and time slot"},
    {"id": "manage-availability", "type": "BusinessProcess", "name": "Manage Availability", "description": "Provider sets available time slots"},
    {"id": "send-reminder", "type": "BusinessProcess", "name": "Send Reminder", "description": "System sends appointment reminders"},
    {"id": "scheduling-service", "type": "BusinessService", "name": "Online Scheduling Service", "description": "Self-service appointment booking capability"},
    {"id": "reminder-service", "type": "BusinessService", "name": "Reminder Service", "description": "Automated appointment reminder notifications"},
    {"id": "appointment", "type": "BusinessObject", "name": "Appointment", "description": "Confirmed booking with date, time, provider"},
    {"id": "time-slot", "type": "BusinessObject", "name": "Time Slot", "description": "Available period for booking"},
    {"id": "patient-record", "type": "BusinessObject", "name": "Patient Record", "description": "Patient demographics and history"}
  ],
  "relationships": [
    {"type": "Serving", "source": "scheduling-service", "target": "patient"},
    {"type": "Serving", "source": "reminder-service", "target": "patient"},
    {"type": "Assignment", "source": "scheduler-role", "target": "book-appointment"},
    {"type": "Assignment", "source": "clinic-staff", "target": "scheduler-role"},
    {"type": "Realization", "source": "book-appointment", "target": "scheduling-service"},
    {"type": "Realization", "source": "send-reminder", "target": "reminder-service"},
    {"type": "Access", "source": "book-appointment", "target": "appointment"},
    {"type": "Access", "source": "book-appointment", "target": "time-slot"},
    {"type": "Access", "source": "manage-availability", "target": "time-slot"},
    {"type": "Flow", "source": "book-appointment", "target": "send-reminder"}
  ]
}
```

## ID Naming Convention

- Use kebab-case: `patient`, `book-appointment`, `scheduling-service`
- Keep IDs short but descriptive
- IDs must be unique within the model
- Use consistent prefixes for clarity: `svc-`, `proc-`, `obj-` (optional)

## Minimum Requirements

1. **At least 5 elements** - Meaningful architecture needs elements
2. **At least 3 relationships** - Elements must be connected
3. **Every element has a description** - For documentation
4. **No orphan elements** - Every element in at least one relationship

## Post-Processing

The JSON output will be transformed to ArchiMate XML using:
```bash
python scripts/json-to-archimate.py input.json output.archimate
```

This produces Archi-compatible XML that can be imported into:
- Archi (open source ArchiMate tool)
- ADOIT (enterprise architecture tool)
- Other ArchiMate 3.1 compatible tools

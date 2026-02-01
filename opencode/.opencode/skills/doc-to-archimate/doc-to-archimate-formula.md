# Plan: Document to ArchiMate Transformation Formula

## Objective
Create a repeatable, step-by-step prompt sequence to transform **any document** (RFD, requirements, process docs) into a valid ArchiMate 3.0 Exchange Format XML model. The process is document-structure agnostic.

---

## Prerequisites

### Reference Files
- **Capability Map**: `opencode/.opencode/skills/adoit-archimate/references/healthcare-capability-model.md`
  - Contains 1666 healthcare capabilities (42 L1, 353 L2, 1042 L3, 229 L4)
  - Used for capability matching in Step 2

### Context Window Management
For large documents, extract intermediate outputs to `.md` files:
- `{project}-step0-parsed.md` - Parsed sentences grouped by structure type
- `{project}-step1-motivation.md` - Motivation layer elements
- `{project}-consolidated.md` - Deduplicated concepts for all subsequent steps

---

## Reference Application Architecture

The Application Layer follows a standard layered architecture. Not all layers may be specified in requirements, but this reference model guides view generation:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                                │
│   ┌─────────────┐    ┌─────────────┐                                    │
│   │  Mobile App │    │  Web Portal │                                    │
│   └──────┬──────┘    └──────┬──────┘                                    │
└──────────┼──────────────────┼───────────────────────────────────────────┘
           │                  │
┌──────────┼──────────────────┼───────────────────────────────────────────┐
│          ▼                  ▼                                            │
│  ┌───────────────┐   ┌─────────────────┐                                │
│  │   Firewall    │──▶│   API Gateway   │     GATEWAY LAYER              │
│  └───────────────┘   └────────┬────────┘                                │
└───────────────────────────────┼─────────────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────────────┐
│                               ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │              IDENTITY & ACCESS MANAGEMENT (IAM)                     ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  SERVICE LAYER (Bounded Contexts / Domains)                              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐           │
│  │  Patient   │ │  Provider  │ │ Appointment│ │Notification│    ...    │
│  │  Domain    │ │  Domain    │ │   Domain   │ │   Domain   │           │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘           │
└────────┼──────────────┼──────────────┼──────────────┼───────────────────┘
         │              │              │              │
┌────────┼──────────────┼──────────────┼──────────────┼───────────────────┐
│        ▼              ▼              ▼              ▼                    │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                  ESB / INTEGRATION LAYER                            ││
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            ││
│  │  │ Adapter  │  │ Adapter  │  │ Adapter  │  │ Adapter  │    ...     ││
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            ││
│  └───────┼─────────────┼─────────────┼─────────────┼───────────────────┘│
└──────────┼─────────────┼─────────────┼─────────────┼────────────────────┘
           │             │             │             │
┌──────────┼─────────────┼─────────────┼─────────────┼────────────────────┐
│          ▼             ▼             ▼             ▼                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │   Daman    │  │  Malaffi   │  │    EMR     │  │   Accela   │   ...  │
│  │  (Insurer) │  │   (HIE)    │  │  Systems   │  │ (Licensing)│        │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘        │
│                      EXTERNAL SYSTEMS LAYER                              │
└─────────────────────────────────────────────────────────────────────────┘

FUTURE ADDITIONS (Data & Analytics Layer):
┌─────────────────────────────────────────────────────────────────────────┐
│  ┌─────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │ ELT/CDC │───▶│ Data        │───▶│  Analytics  │───▶│     ML      │  │
│  │ Pipelines│   │ Warehouse   │    │  Pipelines  │    │   Models    │  │
│  └─────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│                      OLAP / ANALYTICS LAYER                              │
└─────────────────────────────────────────────────────────────────────────┘
```

**Layer Descriptions**:

| Layer | Components | Purpose |
|-------|------------|---------|
| **Presentation** | Mobile App, Web Portal | User interfaces |
| **Gateway** | Firewall (optional), API Gateway | Security, routing, rate limiting |
| **IAM** | Identity & Access Management | Authentication, authorization, SSO |
| **Service** | Bounded Context Domains | Business logic by domain (Patient, Provider, etc.) |
| **ESB/Integration** | Adapters per external system | Protocol translation, data mapping |
| **External** | Backend providers | Daman, Malaffi, EMR, CMS, Licensing |
| **OLAP** (future) | ELT/CDC, DW, Analytics, ML | Reporting, insights, predictions |

**Notes**:
- Not all components may appear in every requirements document
- The reference architecture guides view layout regardless of specified components
- ESB layer is always **horizontal** between Service and External layers
- Each domain in Service layer connects to External systems **through** ESB adapters

---

## 9-Step Transformation Formula

### STEP 0: Parse Document into ArchiMate Structure Groups
**Input**: Any source document (RFD, requirements, process doc, etc.)
**Output**: `{project}-step0-parsed.md` with sentences grouped by ArchiMate structure

**Purpose**: Break document into atomic sentences and classify each by ArchiMate concept type. This enables processing of any document structure.

```
Parse document and group sentences into:

1. ACTIVE STRUCTURE (Who/What performs)
   - Stakeholders: "DOH is responsible for..."
   - Actors: "The user selects...", "Citizens can..."
   - Components: "Sahatna will...", "The system shall..."
   - External systems: "Daman provides...", "Malaffi stores..."

2. PASSIVE STRUCTURE (What is acted upon)
   - Data Objects: "Member card number", "THIQA category", "screening results"
   - Resources: "API provides...", "Data from..."
   - Artifacts: "PDF questionnaire", "HL7 message"

3. BEHAVIOUR (What happens)
   - Processes: "Check eligibility", "Book appointment", "Fill questionnaire"
   - Services: "enables booking", "provides information", "sends reminders"
   - Functions: "validates", "retrieves", "filters", "displays"
   - Events: "After booking...", "When results available...", "7 days after..."

4. MOTIVATION (Why it exists)
   - Drivers: "low engagement", "minimal screenings"
   - Goals: "increase engagement by 75%", "improve health outcomes"
   - Outcomes: "early detection", "timely interventions"
```

**Deduplication**: After grouping, consolidate duplicate/similar concepts:
- Merge "user" + "citizen" + "patient" → single Business Actor
- Merge "booking service" + "appointment booking" → single Business Service
- Create `{project}-consolidated.md` for subsequent steps

---

### STEP 1: Extract Motivation Layer
**Input**: `{project}-consolidated.md` → MOTIVATION group
**Output**: JSON with Stakeholders, Drivers, Goals, Outcomes

```
Extract Motivation Layer elements from consolidated.md:
1. STAKEHOLDERS (id-sh-{shortname}) - from ACTIVE STRUCTURE actors with interest
2. DRIVERS (id-dr-{kebab-case}) - from MOTIVATION section
3. GOALS (id-gl-{kebab-case}) - measurable objectives from MOTIVATION
4. OUTCOMES (id-oc-{kebab-case}) - tangible results from MOTIVATION
```

---

### STEP 2: Extract Strategy Layer
**Input**: `{project}-consolidated.md` + `healthcare-capability-model.md`
**Output**: JSON with Courses of Action, Capabilities, Resources

**IMPORTANT**: Capabilities MUST be matched directly from the Healthcare Provider Reference Model.

```
Extract Strategy Layer elements:

1. COURSES OF ACTION (id-coa-{name})
   - Each addresses one or more OUTCOMES from Step 1
   - Derived from major initiatives/epics in BEHAVIOUR group

2. CAPABILITIES (id-cap-{L1}.{L2}.{L3})
   - Match EXCLUSIVELY against healthcare-capability-model.md
   - Use exact capability names and IDs from reference model
   - Map document concepts to closest L2 or L3 capability

   Matching Process:
   a. List all business functions mentioned in consolidated.md
   b. For each function, search healthcare-capability-model.md
   c. Select matching capability at appropriate level (L2/L3)
   d. Use reference model ID format: "1.1.2" for Patient Registration

   Example Mappings:
   - "eligibility check" → 1.2 Patient Eligibility Management
   - "book appointment" → 5.1 Appointment Scheduling
   - "screening results" → 4.1 Clinical Documentation
   - "notifications" → 10.3 Patient Communication

3. RESOURCES (id-res-{name})
   - External APIs/data sources from PASSIVE STRUCTURE
```

---

### STEP 3: Extract Business Layer
**Input**: `{project}-consolidated.md` → ACTIVE STRUCTURE (actors) + BEHAVIOUR (processes/services)
**Output**: JSON with Actors, Processes, Services

```
Extract Business Layer elements from consolidated.md:
1. BUSINESS ACTORS (id-ba-{name})
   - From ACTIVE STRUCTURE: human actors (users, patients, staff)
   - Exclude system components (those go to Application Layer)

2. BUSINESS PROCESSES (id-bp-{name})
   - From BEHAVIOUR: user journey steps
   - Sequence: Check eligibility → Select package → Choose facility → Book appointment

3. BUSINESS SERVICES (id-bs-{name})
   - From BEHAVIOUR: services exposed to actors
   - Link to Capabilities from Step 2
```

---

### STEP 4: Extract Application Layer
**Input**: `{project}-consolidated.md` + Reference Architecture template
**Output**: `{project}-application.json` with Components, Services, Interfaces, Functions, Data, Events

**Reference Architecture Mapping** (not all may be specified in requirements):

```
Extract Application Layer elements, mapped to reference architecture:

BY LAYER:

1. PRESENTATION LAYER
   - id-ac-mobile: Mobile Application (if mentioned)
   - id-ac-web: Web Portal (if mentioned)

2. GATEWAY LAYER
   - id-ac-firewall: Firewall (optional, if security mentioned)
   - id-ac-gateway: API Gateway

3. IAM LAYER
   - id-ac-identity: Identity & Access Management

4. SERVICE LAYER (Bounded Contexts by Domain)
   - id-ac-patient: Patient Domain
   - id-ac-provider: Provider Domain
   - id-ac-appointment: Appointment Domain
   - id-ac-notification: Notification Domain
   - id-ac-{domain}: Additional domains from requirements

5. ESB/INTEGRATION LAYER
   - id-ac-integration: Integration/ESB Component
   - id-ai-{ext}-adapter: Adapter Interface per external system

6. EXTERNAL SYSTEMS LAYER
   - id-ac-ext-{name}: External backend systems (Daman, Malaffi, EMR, etc.)

7. (FUTURE) OLAP LAYER
   - id-ac-etl: ELT/CDC Pipelines
   - id-ac-dw: Data Warehouse
   - id-ac-analytics: Analytics Pipelines
   - id-ac-ml: ML Models

BY ELEMENT TYPE:

- APPLICATION SERVICES (id-as-{name})
  APIs/capabilities exposed by components

- APPLICATION INTERFACES (id-ai-{name}, id-ai-ext-{name})
  Access points; each component has one interface

- APPLICATION FUNCTIONS (id-af-{name})
  Processing logic: "validates", "retrieves", "filters"

- DATA OBJECTS (id-do-{name})
  Key data entities from PASSIVE STRUCTURE

- APPLICATION EVENTS (id-ae-{name})
  Async triggers: "After...", "When...", "triggers..."
```

**Note**: Only include components explicitly mentioned in requirements. The reference architecture guides layout, but don't invent unmentioned components.

---

### STEP 5: Generate Relationships
**Input**: All elements from Steps 1-4 (JSON files)
**Output**: `{project}-relationships.json` array of relationships (id-rel-{nnn})

**Relationship Rules by Layer**:

| Layer | Source | Target | Type | Notes |
|-------|--------|--------|------|-------|
| **Motivation** | Stakeholder | Driver | Association | |
| **Motivation** | Driver | Goal | Influence | |
| **Motivation** | Outcome | Goal | Realization | |
| **Strategy** | CourseOfAction | Outcome | Realization | CoA achieves Outcome |
| **Strategy** | Capability | CourseOfAction | Realization | |
| **Business** | BusinessProcess | Capability | Realization | |
| **Business→App** | ApplicationService | BusinessProcess | Serving | |
| **Application** | Component | Interface | Composition | Component owns Interface |
| **Application** | Interface | Service | Assignment | Interface exposes Service |
| **Application** | Function | Service | Realization | Function implements Service |
| **Application** | Component | Function | Assignment | Component has Function |
| **Application** | Function | DataObject | Access | read/write |
| **Application** | Function | Event | Triggering | |
| **Application** | Interface | Interface | Flow | **Gateway flows through Interfaces, not Components** |

**Critical Semantic Rules**:
1. **Gateway Pattern**: Mobile/Web → Gateway Interface (not Component)
2. **Domain Serving**: Domain Interface → Gateway Interface (not Component → Component)
3. **ESB/Integration**: Horizontal layer between internal domains and external systems
4. **External Access**: Internal Interface → ESB Adapter Interface → External Interface

---

### STEP 6: Generate Organizations
**Input**: All JSON files from Steps 1-5
**Output**: XML `<organizations>` section

```xml
<organizations>
  <item><label>Motivation</label><!-- stakeholders, drivers, goals, outcomes --></item>
  <item><label>Strategy</label><!-- coa, capabilities, resources --></item>
  <item><label>Business</label><!-- processes, services, actors --></item>
  <item><label>Application</label><!-- components, services, interfaces, functions, data, events --></item>
  <item><label>Relations</label><!-- all relationship refs --></item>
</organizations>
```

---

### STEP 7: Generate Views
**Input**: All JSON files from Steps 1-5 + Organizations from Step 6
**Output**: XML `<views>` section with diagram layouts

**Standard Views**:
1. `id-view-motivation` - Stakeholder/Driver/Goal/Outcome cascade
2. `id-view-strategy` - Capabilities and Courses of Action
3. `id-view-capability-map` - Grid of business capabilities
4. `id-view-process` - Business process flow
5. `id-view-application` - Complete application architecture (reference model)
6. `id-view-integration` - External system connections

**View 5: Application Architecture Layout** (based on Reference Architecture):

```
Y Position   Layer Content
---------    -------------
y=0          PRESENTATION: Mobile App, Web Portal (side by side)
y=120        GATEWAY: Firewall (optional), API Gateway
y=240        IAM: Identity & Access Management (full width)
y=360        SERVICE LAYER: Bounded Context Domains (side by side)
             - Patient, Provider, Appointment, Integration, etc.
y=600        ESB: Integration Layer with Adapters (horizontal, full width)
y=720        EXTERNAL: Backend provider systems (side by side)
y=900        (future) OLAP: ELT/CDC, DW, Analytics, ML
```

**Layout Rules**:
- Row spacing: 120px vertical gap between layers
- Column spacing: 200px horizontal gap between components
- Node sizes:
  - Components: 180x60
  - Interfaces: 180x45
  - Functions: 85x40
  - Groupings: 100% width of contained elements + 40px padding
- Layer groupings use nested boxes to show containment
- ESB layer spans full width (horizontal integration pattern)

**Standard ArchiMate Color Palette**:

| Layer | Element Type | Color | Hex |
|-------|--------------|-------|-----|
| **Motivation** | Stakeholder, Driver, Goal, Outcome | Purple/Violet | #CCCCFF |
| **Strategy** | Capability, CourseOfAction, Resource | Beige/Tan | #F5DEB3 |
| **Business** | Actor, Process, Service, Object | Yellow | #FFFFB5 |
| **Application** | Component, Function | Light Blue | #B5D3E7 |
| **Application** | Interface | Light Blue (border) | #9BC4E2 |
| **Application** | Service | Yellow | #FFFFB5 |
| **Application** | Data Object | Green | #C9E7B5 |
| **Application** | Event | Orange | #FFB5B5 |
| **Technology** | Node, Device, Network | Green | #C9E7B5 |
| **External** | All external elements | Gray | #D5D5D5 |

*These match ArchiMate 3.0 standard layer colors for consistency with Archi and ADOIT defaults.*

---

### STEP 8: Assemble Final XML
**Input**: All JSON outputs + Organizations XML + Views XML
**Output**: `{project}.xml` - Complete ArchiMate Exchange Format XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.opengroup.org/xsd/archimate/3.0/ http://www.opengroup.org/xsd/archimate/3.1/archimate3_Diagram.xsd"
       identifier="id-{project}-model-001">
  <name xml:lang="en">{Project Name}</name>
  <documentation xml:lang="en">{Description}</documentation>
  <elements><!-- All elements --></elements>
  <relationships><!-- All relationships --></relationships>
  <organizations><!-- Folder structure --></organizations>
  <views><diagrams><!-- All views --></diagrams></views>
</model>
```

---

## ID Naming Convention Reference

| RFD Section | Element Type | ID Pattern | Example |
|-------------|--------------|------------|---------|
| Stakeholders | Stakeholder | `id-sh-{name}` | `id-sh-doh` |
| Key Drivers | Driver | `id-dr-{name}` | `id-dr-low-participation` |
| Objectives | Goal | `id-gl-{name}` | `id-gl-increase-engagement` |
| Expected Results | Outcome | `id-oc-{name}` | `id-oc-higher-uptake` |
| Epics | CourseOfAction | `id-coa-{name}` | `id-coa-digital-eligibility` |
| Capabilities | Capability | `id-cap-{name}` | `id-cap-patient-mgmt` |
| APIs/Data | Resource | `id-res-{name}` | `id-res-daman-api` |
| Journey Steps | BusinessProcess | `id-bp-{name}` | `id-bp-check-eligibility` |
| Services | BusinessService | `id-bs-{name}` | `id-bs-booking` |
| Users | BusinessActor | `id-ba-{name}` | `id-ba-citizen` |
| Modules | ApplicationComponent | `id-ac-{name}` | `id-ac-patient` |
| External | ApplicationComponent | `id-ac-ext-{name}` | `id-ac-ext-daman` |
| API Services | ApplicationService | `id-as-{name}` | `id-as-eligibility` |
| Internal IF | ApplicationInterface | `id-ai-{name}` | `id-ai-patient-api` |
| External IF | ApplicationInterface | `id-ai-ext-{name}` | `id-ai-ext-daman` |
| Functions | ApplicationFunction | `id-af-{name}` | `id-af-authenticate` |
| Data | DataObject | `id-do-{name}` | `id-do-patient` |
| Events | ApplicationEvent | `id-ae-{name}` | `id-ae-booking-created` |
| Groups | Grouping | `id-grp-{name}` | `id-grp-identity` |
| Relations | Relationship | `id-rel-{nnn}` | `id-rel-001` |

---

## Validation Checklist

### Per-Step Validation
- [ ] Step 0: All sentences classified into structure groups
- [ ] Step 0: Consolidated.md has no duplicate concepts
- [ ] Step 2: All capabilities matched to healthcare-capability-model.md (no invented capabilities)
- [ ] Step 5: All relationship source/target elements exist

### Final Validation
- [ ] All IDs are unique across all elements
- [ ] All organization refs point to existing elements
- [ ] All view elementRefs point to existing elements
- [ ] XML is well-formed and validates against ArchiMate 3.0 schema
- [ ] Gateway relationships flow through Interfaces (not Components)
- [ ] ESB layer is horizontal (between domains and externals)

**Traceability Check** (verify all chains complete):
```
Stakeholder ─[Association]→ Driver ─[Influence]→ Goal ←[Realization]─ Outcome
                                                            ↑
                                      CourseOfAction ─[Realization]─┘
                                            ↑
                                 Capability ─[Realization]─┘
                                      ↑
                          BusinessProcess ─[Realization]─┘
                                 ↑
                    ApplicationService ─[Serving]─┘
```

**Capability Verification**:
```
Every Capability ID must exist in healthcare-capability-model.md
Example: id-cap-1.2.3 → verify "1.2.3" exists in reference model
```

---

## Files Reference
- **Source Document**: Any document (RFD, requirements, process spec)
- **Capability Map**: `opencode/.opencode/skills/adoit-archimate/references/healthcare-capability-model.md`
- **Example RFD**: `RFD_IFHAS_V3.md` (reference structure)
- **Example Output**: `IFHAS Preventive Screening Initiative.xml` (reference XML)

## Intermediate Files (Context Window Management)
When processing large documents, create these intermediate files:

| Step | File | Purpose |
|------|------|---------|
| 0 | `{project}-step0-parsed.md` | Sentences grouped by structure type |
| 0 | `{project}-consolidated.md` | Deduplicated concepts (input for Steps 1-4) |
| 1 | `{project}-motivation.json` | Motivation layer elements |
| 2 | `{project}-strategy.json` | Strategy layer with matched capabilities |
| 3 | `{project}-business.json` | Business layer elements |
| 4 | `{project}-application.json` | Application layer elements |
| 5 | `{project}-relationships.json` | All relationships |
| 8 | `{project}.xml` | Final ArchiMate Exchange Format |

**Recommendation**: For documents >5 pages, always extract to intermediate files. This enables:
- Review and validation at each step
- Resumption if context window exhausted
- Collaborative editing of extracted concepts

## Verification
1. Open generated XML in Archi or ADOIT
2. Verify all layers populated correctly
3. Check relationship arrows follow correct semantics
4. Validate Gateway→Interface (not Component) flows
5. Confirm ESB layer horizontal between domains and externals

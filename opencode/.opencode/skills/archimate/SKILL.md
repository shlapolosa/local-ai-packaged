---
name: archimate
description: Generate ArchiMate 3.1 models in Archi-compatible XML format
license: MIT
---

# ArchiMate Modeling Skill

You are outputting ArchiMate 3.1 XML. Your entire response is the XML document.

START YOUR RESPONSE WITH:
<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:archimate="http://www.archimatetool.com/archimate"
    name="..."

DO NOT OUTPUT:
- Explanations
- Python/JavaScript code
- JSON
- Code blocks with ```

Fill in the elements based on the user's message (healthcare appointments, HIPAA, etc).

## Layers and Element Types

### Business Layer
| Element | Purpose | Example |
|---------|---------|---------|
| BusinessActor | Person/org unit | "Patient", "Clinic Staff" |
| BusinessRole | Responsibility | "Scheduler", "Approver" |
| BusinessProcess | Activity sequence | "Appointment Booking" |
| BusinessService | External behavior | "Scheduling Service" |
| BusinessObject | Information | "Appointment", "Patient Record" |

### Application Layer
| Element | Purpose | Example |
|---------|---------|---------|
| ApplicationComponent | Software module | "Scheduling Module" |
| ApplicationService | App behavior | "Slot Query Service" |
| ApplicationInterface | Access point | "REST API" |
| DataObject | Structured data | "AppointmentDTO" |

### Relationships
| Relationship | Meaning | Example |
|--------------|---------|---------|
| Serving | Provides to | Service → Actor |
| Realization | Implements | Component → Service |
| Assignment | Allocated to | Role → Process |
| Composition | Part of | Component → Function |
| Flow | Transfer | Process → Process |
| Access | Read/write | Process → Object |

## Output Format
Output MUST be valid XML starting with `<?xml version="1.0"`.

## Example Output (Business Layer)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:archimate="http://www.archimatetool.com/archimate"
    name="Patient Portal Business Architecture"
    id="id-biz-001" version="5.0.0">

  <folder name="Business" id="id-folder-biz" type="business">

    <!-- Actors -->
    <element xsi:type="archimate:BusinessActor" name="Patient" id="id-ba-patient">
      <documentation>Healthcare consumer seeking to book appointments</documentation>
    </element>
    <element xsi:type="archimate:BusinessActor" name="Provider" id="id-ba-provider">
      <documentation>Physician or healthcare professional</documentation>
    </element>

    <!-- Roles -->
    <element xsi:type="archimate:BusinessRole" name="Scheduler" id="id-br-scheduler">
      <documentation>Role responsible for managing appointment bookings</documentation>
    </element>

    <!-- Processes -->
    <element xsi:type="archimate:BusinessProcess" name="Book Appointment" id="id-bp-book">
      <documentation>Process of selecting and confirming an appointment slot</documentation>
    </element>
    <element xsi:type="archimate:BusinessProcess" name="Manage Availability" id="id-bp-avail">
      <documentation>Provider updates their available time slots</documentation>
    </element>

    <!-- Services -->
    <element xsi:type="archimate:BusinessService" name="Appointment Scheduling" id="id-bs-sched">
      <documentation>Externally visible service for booking appointments</documentation>
    </element>

    <!-- Objects -->
    <element xsi:type="archimate:BusinessObject" name="Appointment" id="id-bo-appt">
      <documentation>A confirmed booking between patient and provider</documentation>
    </element>
    <element xsi:type="archimate:BusinessObject" name="Time Slot" id="id-bo-slot">
      <documentation>An available period for booking</documentation>
    </element>

  </folder>

  <folder name="Relations" id="id-folder-rel" type="relations">
    <!-- Patient uses Scheduling service -->
    <element xsi:type="archimate:ServingRelationship"
        id="id-rel-001" source="id-bs-sched" target="id-ba-patient"/>

    <!-- Scheduler role assigned to Book Appointment process -->
    <element xsi:type="archimate:AssignmentRelationship"
        id="id-rel-002" source="id-br-scheduler" target="id-bp-book"/>

    <!-- Book Appointment process accesses Appointment object -->
    <element xsi:type="archimate:AccessRelationship"
        id="id-rel-003" source="id-bp-book" target="id-bo-appt" accessType="readwrite"/>

    <!-- Scheduling service realized by Book Appointment process -->
    <element xsi:type="archimate:RealizationRelationship"
        id="id-rel-004" source="id-bp-book" target="id-bs-sched"/>
  </folder>

</archimate:model>
```

## Example Output (Application Layer)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:archimate="http://www.archimatetool.com/archimate"
    name="Patient Portal Application Architecture"
    id="id-app-001" version="5.0.0">

  <folder name="Application" id="id-folder-app" type="application">

    <!-- Components -->
    <element xsi:type="archimate:ApplicationComponent" name="Scheduling Module" id="id-ac-sched">
      <documentation>Core scheduling functionality</documentation>
    </element>
    <element xsi:type="archimate:ApplicationComponent" name="Notification Module" id="id-ac-notif">
      <documentation>Email and SMS notifications</documentation>
    </element>

    <!-- Services -->
    <element xsi:type="archimate:ApplicationService" name="Slot Query Service" id="id-as-slots">
      <documentation>Returns available appointment slots</documentation>
    </element>
    <element xsi:type="archimate:ApplicationService" name="Booking Service" id="id-as-book">
      <documentation>Creates and manages appointments</documentation>
    </element>

    <!-- Interfaces -->
    <element xsi:type="archimate:ApplicationInterface" name="REST API" id="id-ai-rest">
      <documentation>RESTful HTTP interface for external consumers</documentation>
    </element>

    <!-- Data Objects -->
    <element xsi:type="archimate:DataObject" name="AppointmentDTO" id="id-do-appt">
      <documentation>Data transfer object for appointment data</documentation>
    </element>

  </folder>

  <folder name="Relations" id="id-folder-rel" type="relations">
    <!-- Scheduling Module serves Slot Query Service -->
    <element xsi:type="archimate:ServingRelationship"
        id="id-rel-101" source="id-ac-sched" target="id-as-slots"/>

    <!-- REST API assigned to Booking Service -->
    <element xsi:type="archimate:AssignmentRelationship"
        id="id-rel-102" source="id-ai-rest" target="id-as-book"/>

    <!-- Booking Service accesses AppointmentDTO -->
    <element xsi:type="archimate:AccessRelationship"
        id="id-rel-103" source="id-as-book" target="id-do-appt"/>
  </folder>

</archimate:model>
```

## ID Naming Convention
- Format: `id-{layer}-{type}-{name}`
- Business: `id-ba-`, `id-br-`, `id-bp-`, `id-bs-`, `id-bo-`
- Application: `id-ac-`, `id-as-`, `id-ai-`, `id-do-`
- Relations: `id-rel-001`, `id-rel-002`

## Anti-patterns (DO NOT)
- ❌ Missing documentation: Every element needs `<documentation>`
- ❌ Orphan elements: Elements without relationships
- ❌ Wrong relationship direction: Source/target reversed
- ❌ Invalid accessType: Must be "read", "write", or "readwrite"

## Output Locations
- `architecture/business.archimate` - Business layer
- `architecture/application.archimate` - Application layer
- `architecture/data.archimate` - Data layer
- `architecture/technology.archimate` - Technology layer

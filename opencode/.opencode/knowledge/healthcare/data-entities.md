# Healthcare Data Entities

This document defines the core data entities for healthcare provider systems, aligned with HL7 FHIR R4 standards.

## Core Clinical Entities

### Patient
The individual receiving healthcare services.

**Key Attributes**:
- `identifier`: MRN, SSN, insurance IDs
- `name`: Legal name, preferred name
- `birthDate`: Date of birth
- `gender`: Administrative gender
- `address`: Residential, mailing addresses
- `telecom`: Phone, email, fax
- `contact`: Emergency contacts
- `communication`: Preferred language
- `generalPractitioner`: Primary care provider reference

**FHIR Resource**: `Patient`

### Encounter
A patient interaction with the healthcare system.

**Key Attributes**:
- `identifier`: Visit number, account number
- `status`: planned, in-progress, finished, cancelled
- `class`: inpatient, outpatient, emergency, virtual
- `type`: Visit type (annual exam, follow-up, etc.)
- `subject`: Patient reference
- `participant`: Providers involved
- `period`: Start and end times
- `location`: Where encounter occurred
- `serviceProvider`: Organization reference

**FHIR Resource**: `Encounter`

### Practitioner
Healthcare provider (physician, nurse, etc.)

**Key Attributes**:
- `identifier`: NPI, DEA, state license
- `name`: Provider name
- `telecom`: Contact information
- `address`: Practice address
- `qualification`: Credentials, certifications
- `communication`: Languages spoken

**FHIR Resource**: `Practitioner`

### Organization
Healthcare organization (hospital, clinic, practice)

**Key Attributes**:
- `identifier`: NPI, TIN
- `name`: Organization name
- `type`: Hospital, clinic, pharmacy
- `telecom`: Contact information
- `address`: Locations
- `partOf`: Parent organization

**FHIR Resource**: `Organization`

## Clinical Documentation

### Condition
Diagnosis or health concern.

**Key Attributes**:
- `clinicalStatus`: active, recurrence, relapse, inactive, remission, resolved
- `verificationStatus`: confirmed, provisional, differential
- `category`: Problem list, encounter diagnosis
- `severity`: Mild, moderate, severe
- `code`: ICD-10, SNOMED CT code
- `subject`: Patient reference
- `encounter`: Related encounter
- `onset`: When condition started
- `recordedDate`: When documented

**FHIR Resource**: `Condition`

### Observation
Clinical measurements and findings.

**Key Attributes**:
- `status`: registered, preliminary, final, amended
- `category`: Vital signs, laboratory, imaging
- `code`: LOINC code
- `subject`: Patient reference
- `encounter`: Related encounter
- `effectiveDateTime`: When observed
- `value`: Result value (quantity, string, code)
- `interpretation`: High, low, normal
- `referenceRange`: Normal ranges

**FHIR Resource**: `Observation`

### DiagnosticReport
Results from diagnostic procedures.

**Key Attributes**:
- `status`: registered, partial, preliminary, final
- `category`: Laboratory, radiology, pathology
- `code`: Report type
- `subject`: Patient reference
- `encounter`: Related encounter
- `effectiveDateTime`: When performed
- `result`: Observation references
- `conclusion`: Clinical interpretation
- `presentedForm`: Attached report document

**FHIR Resource**: `DiagnosticReport`

### Procedure
Clinical procedures performed.

**Key Attributes**:
- `status`: preparation, in-progress, completed
- `category`: Surgical, diagnostic, therapeutic
- `code`: CPT, SNOMED procedure code
- `subject`: Patient reference
- `encounter`: Related encounter
- `performer`: Who performed
- `location`: Where performed
- `outcome`: Result of procedure

**FHIR Resource**: `Procedure`

## Medication Management

### Medication
Drug or substance.

**Key Attributes**:
- `code`: RxNorm, NDC code
- `form`: Tablet, capsule, injection
- `amount`: Package size
- `ingredient`: Active ingredients

**FHIR Resource**: `Medication`

### MedicationRequest
Prescription or order for medication.

**Key Attributes**:
- `status`: active, completed, cancelled
- `intent`: order, plan, proposal
- `medication`: Drug reference
- `subject`: Patient reference
- `encounter`: Related encounter
- `requester`: Ordering provider
- `dosageInstruction`: How to take
- `dispenseRequest`: Quantity, refills

**FHIR Resource**: `MedicationRequest`

### MedicationAdministration
Record of medication given.

**Key Attributes**:
- `status`: completed, not-done
- `medication`: Drug reference
- `subject`: Patient reference
- `encounter`: Related encounter
- `effectiveDateTime`: When administered
- `performer`: Who administered
- `dosage`: Amount given

**FHIR Resource**: `MedicationAdministration`

## Scheduling

### Appointment
Scheduled healthcare encounter.

**Key Attributes**:
- `status`: proposed, pending, booked, arrived, fulfilled, cancelled
- `serviceType`: Type of appointment
- `specialty`: Provider specialty
- `appointmentType`: Routine, follow-up, urgent
- `start`: Appointment start time
- `end`: Appointment end time
- `participant`: Patient, provider, location

**FHIR Resource**: `Appointment`

### Schedule
Provider availability.

**Key Attributes**:
- `actor`: Provider or location
- `planningHorizon`: Available date range
- `comment`: Scheduling notes

**FHIR Resource**: `Schedule`

### Slot
Available time segment.

**Key Attributes**:
- `schedule`: Parent schedule
- `status`: free, busy, busy-unavailable
- `start`: Slot start time
- `end`: Slot end time

**FHIR Resource**: `Slot`

## Financial

### Coverage
Insurance coverage.

**Key Attributes**:
- `status`: active, cancelled
- `type`: Medical, dental, vision
- `subscriber`: Policyholder
- `beneficiary`: Covered patient
- `payor`: Insurance organization
- `class`: Plan, group information
- `period`: Coverage dates

**FHIR Resource**: `Coverage`

### Claim
Billing claim submission.

**Key Attributes**:
- `status`: active, cancelled
- `type`: Institutional, professional, pharmacy
- `use`: claim, preauthorization
- `patient`: Patient reference
- `provider`: Billing provider
- `insurer`: Payer reference
- `diagnosis`: Diagnoses for claim
- `procedure`: Procedures for claim
- `item`: Line items

**FHIR Resource**: `Claim`

## Common Code Systems

| Domain | Code System | Example |
|--------|-------------|---------|
| Diagnoses | ICD-10-CM | E11.9 (Type 2 Diabetes) |
| Diagnoses | SNOMED CT | 44054006 (Type 2 Diabetes) |
| Procedures | CPT | 99213 (Office Visit) |
| Procedures | HCPCS | G0438 (Annual Wellness Visit) |
| Laboratory | LOINC | 2345-7 (Glucose) |
| Medications | RxNorm | 860975 (Metformin 500mg) |
| Medications | NDC | 0093-7212-01 |

## Data Relationships

```
Patient
  ├── Encounter[]
  │     ├── Condition[]
  │     ├── Observation[]
  │     ├── Procedure[]
  │     └── MedicationAdministration[]
  ├── MedicationRequest[]
  ├── Appointment[]
  ├── Coverage[]
  └── Claim[]

Practitioner
  ├── performs → Encounter
  ├── requests → MedicationRequest
  └── participant → Appointment

Organization
  ├── employs → Practitioner
  ├── hosts → Encounter
  └── receives → Claim
```

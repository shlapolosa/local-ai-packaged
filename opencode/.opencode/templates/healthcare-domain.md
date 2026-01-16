# Healthcare Domain Knowledge

## FHIR R4 Resources

**Administrative:**
- Patient, Practitioner, PractitionerRole, Organization
- Location, HealthcareService, Endpoint

**Clinical:**
- Encounter, Appointment, Schedule, Slot
- Observation, DiagnosticReport, Condition, Procedure
- AllergyIntolerance, FamilyMemberHistory, ClinicalImpression

**Medications:**
- MedicationRequest, MedicationDispense, MedicationAdministration
- MedicationStatement, Immunization

**Financial:**
- Coverage, Claim, ClaimResponse, ExplanationOfBenefit

**Workflow:**
- Task, ServiceRequest, CommunicationRequest
- CarePlan, Goal, NutritionOrder

**Security:**
- Consent, AuditEvent, Provenance

## Common Healthcare Patterns

### Patient Management
- Patient matching and linking (MPI)
- Patient merge/unmerge operations
- Demographics management
- Insurance eligibility verification

### Clinical Workflows
- Order entry (CPOE) for labs, radiology, pharmacy
- Results management and review
- Clinical documentation (notes, assessments)
- Clinical decision support (CDS) integration
- Referral management

### Documentation
- Clinical document generation (CDA)
- Structured data capture (SDC)
- Template-based documentation
- Signature and attestation workflows

### Integration Patterns
- HL7 v2 message processing
- FHIR RESTful operations
- CDS Hooks integration
- SMART on FHIR app launch

## UAE Healthcare Integration

### NABIDH (Dubai)
- FHIR R4 based HIE
- Patient demographics sync
- Clinical summary exchange
- Lab results sharing
- Prescription information

### Malaffi (Abu Dhabi)
- IHE profile based
- XDS document sharing
- Patient index (PIX/PDQ)
- Cross-community access (XCA)

### Other Integrations
- TAMM government services
- Insurance aggregators (DHA, HAAD)
- Emirates ID verification
- Unified prescription system

## Compliance Requirements

### ADHICS (Abu Dhabi Health Information and Cyber Security)
- Security control framework
- Risk assessment requirements
- Incident response procedures
- Access control requirements

### Data Protection
- Patient consent management
- Data residency (UAE territory)
- Data retention policies
- Right to access/erasure

### Audit Requirements
- All PHI access logged
- User action audit trail
- Data modification history
- Login/logout tracking

### Access Control
- Role-based access control (RBAC)
- Break-the-glass procedures
- Minimum necessary access
- Patient-provider relationship validation

## Rubric Categories for Healthcare

### FHIR Standards (fhir_standards)
- 0: No FHIR involvement
- 1: Read existing FHIR resources
- 2: Create/update standard resources
- 3: Complex resource operations
- 5: Custom profiles/extensions
- 8: Multi-resource transactions
- 13: HIE integration complexity

### Clinical Workflow (clinical_workflow)
- 0: No clinical impact
- 1: Simple clinical data display
- 2: Clinical data entry
- 3: Order workflows
- 5: Decision support integration
- 8: Complex clinical processes
- 13: Cross-department workflows

### Compliance (compliance)
- 0: No PHI/compliance impact
- 1: Basic audit logging
- 2: Access control implementation
- 3: Consent management
- 5: Regulatory reporting
- 8: Multi-jurisdiction compliance
- 13: Full ADHICS audit

### Interoperability (interoperability)
- 0: No external integration
- 1: Single external API
- 2: Standard protocol (HL7/FHIR)
- 3: Multiple external systems
- 5: HIE connection (NABIDH/Malaffi)
- 8: Bidirectional sync
- 13: Real-time multi-system orchestration

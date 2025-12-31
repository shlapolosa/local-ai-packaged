# Healthcare Component Types

This document defines common application component types for healthcare provider systems.

## Clinical Systems

### Electronic Health Record (EHR)
Core clinical documentation system.

**Capabilities**:
- Patient demographics management
- Clinical documentation
- Order entry (CPOE)
- Results review
- Medication management
- Problem list management

**Integration Points**:
- HL7 FHIR R4 APIs
- HL7 v2 ADT, ORU, ORM messages
- CCDA document exchange
- Direct messaging

**Common Products**: Epic, Cerner, MEDITECH, Allscripts

### Practice Management System (PMS)
Administrative and billing functions.

**Capabilities**:
- Patient registration
- Scheduling
- Insurance verification
- Claim submission
- Payment processing
- Reporting

**Integration Points**:
- HL7 v2 scheduling messages
- X12 EDI (837, 835, 270/271)
- Real-time eligibility APIs

### Laboratory Information System (LIS)
Laboratory order and result management.

**Capabilities**:
- Order management
- Specimen tracking
- Result entry and validation
- Quality control
- Reference lab interfaces

**Integration Points**:
- HL7 v2 ORM, ORU messages
- LOINC coding
- Instrument interfaces

### Radiology Information System (RIS) / PACS
Imaging order and storage.

**Capabilities**:
- Imaging order management
- Study tracking
- Image storage (PACS)
- Radiologist worklist
- Report distribution

**Integration Points**:
- DICOM image transfer
- HL7 v2 ORM, ORU messages
- IHE XDS-I profiles

### Pharmacy System
Medication dispensing and management.

**Capabilities**:
- Prescription processing
- Drug inventory
- Dispensing workflow
- Drug interaction checking
- Controlled substance tracking

**Integration Points**:
- NCPDP SCRIPT (e-prescribing)
- HL7 v2 RDE messages
- State PDMP reporting

## Patient Engagement

### Patient Portal
Patient self-service platform.

**Capabilities**:
- Appointment scheduling
- Secure messaging
- Test result viewing
- Bill payment
- Medical record access
- Prescription refill requests

**Integration Points**:
- FHIR Patient Access API
- OAuth 2.0 / SMART on FHIR
- Direct secure messaging

### Telehealth Platform
Virtual care delivery.

**Capabilities**:
- Video visits
- Asynchronous consults
- Remote patient monitoring device integration
- Virtual waiting room
- Documentation capture

**Integration Points**:
- EHR scheduling integration
- FHIR encounter creation
- Device data ingestion

### Mobile Health App
Patient mobile application.

**Capabilities**:
- Appointment management
- Medication reminders
- Health tracking
- Push notifications
- Biometric authentication

**Integration Points**:
- FHIR mobile APIs
- Apple HealthKit / Google Fit
- Push notification services

## Care Coordination

### Care Management Platform
Population health and care coordination.

**Capabilities**:
- Care plan management
- Risk stratification
- Care gap identification
- Transitions of care
- Community resource referrals

**Integration Points**:
- ADT notifications (HL7 v2)
- FHIR CareTeam, CarePlan
- SDOH assessments

### Health Information Exchange (HIE)
Cross-organization data sharing.

**Capabilities**:
- Patient record lookup
- Document exchange
- Event notifications
- Master patient index

**Integration Points**:
- IHE XDS/XCA profiles
- FHIR exchange
- Direct messaging
- TEFCA QHIN connectivity

### Referral Management
Specialist referral coordination.

**Capabilities**:
- Referral creation and tracking
- Specialist directory
- Authorization management
- Appointment coordination
- Feedback loop

**Integration Points**:
- FHIR ServiceRequest
- HL7 v2 REF messages
- Fax integration

## Revenue Cycle

### Revenue Cycle Management (RCM)
End-to-end billing operations.

**Capabilities**:
- Charge capture
- Coding assistance
- Claim scrubbing
- Denial management
- Collections
- Analytics and reporting

**Integration Points**:
- Charge data (HL7 v2 DFT)
- X12 EDI transactions
- Clearinghouse APIs

### Prior Authorization System
Insurance authorization management.

**Capabilities**:
- Authorization request submission
- Status tracking
- Rule-based routing
- Payer portal integration
- Documentation attachment

**Integration Points**:
- X12 278 transactions
- FHIR Prior Auth
- Payer APIs

### Patient Financial Services
Patient payment and assistance.

**Capabilities**:
- Cost estimation
- Payment plans
- Financial assistance screening
- Patient statements
- Online bill pay

**Integration Points**:
- Payment gateway APIs
- EHR demographic sync
- Charity care databases

## Infrastructure

### Identity and Access Management (IAM)
User authentication and authorization.

**Capabilities**:
- Single sign-on (SSO)
- Multi-factor authentication
- Role-based access control
- Privileged access management
- User provisioning

**Integration Points**:
- SAML 2.0
- OAuth 2.0 / OpenID Connect
- LDAP/Active Directory
- SCIM user provisioning

### Integration Engine
Message routing and transformation.

**Capabilities**:
- Protocol translation
- Message routing
- Data transformation
- Error handling
- Monitoring and alerting

**Integration Points**:
- HL7 v2 TCP/MLLP
- FHIR REST
- X12 EDI
- File-based (SFTP)

**Common Products**: MuleSoft, Rhapsody, InterSystems HealthShare

### Data Warehouse / Analytics
Clinical and operational analytics.

**Capabilities**:
- Data aggregation
- Quality metrics (HEDIS, CMS)
- Population analytics
- Operational dashboards
- Predictive modeling

**Integration Points**:
- ETL from source systems
- FHIR Bulk Data Export
- BI tool connections

## OAM Component Mapping

For OAM/KubeVela deployments:

| Component Type | OAM Workload | Traits |
|---------------|--------------|--------|
| Patient Portal | webservice | ingress, scaler, gateway |
| API Gateway | webservice | ingress, ratelimit, auth |
| EHR Integration | worker | configmap, secret |
| Message Queue | statefulset | storage, backup |
| Database | database | backup, replication |
| Analytics | cronjob | configmap |

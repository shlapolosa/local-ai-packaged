---
doc_id: sahatna-doh-integration
component_name: DOH
component_type: external
is_internal: false
document_type: external-integration
project: Sahatna Super App
integration: DOH
internal_systems:
- Patient Service
- Provider Service
- Batch-worker Service
capabilities:
- patient data retrieval
- license validation
- provider verification
integrations:
- DOH
- Department of Health
- DOH Patient Info System
- DOH Licenses Info System
- MOI
- Ministry of Interior
---

# Department of Health (DOH) Integrations

## DoH Patient Info System
Centralized patient information management system that stores and manages comprehensive patient medical records, demographics, and health data. Enables healthcare providers to access patient information across the healthcare network for continuity of care.
- Integration: SOAP API
- Internal connection to MOI (Ministry of Interior)
- Used by: Patient Service Module

## DoH Licenses Info System
Database system that manages and tracks professional licenses for healthcare providers, facilities, and medical practitioners.
- Maintains licensing status and renewals
- Tracks qualifications and regulatory compliance
- Information for all healthcare entities within jurisdiction
- Integration: SOAP API
- Used by: Provider Service Module, Batch-worker Service

## Data Types
- Patient personal information
- Physician license data
- Facility license data
- Healthcare provider qualifications

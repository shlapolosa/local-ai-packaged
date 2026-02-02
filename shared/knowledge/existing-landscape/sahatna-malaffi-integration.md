---
doc_id: sahatna-malaffi-integration
component_name: Malaffi
component_type: external
is_internal: false
document_type: external-integration
project: Sahatna Super App
integration: Malaffi
internal_systems:
- PHR Service
- Integration Service
- Patient Service
capabilities:
- health records
- PHR
- HIE
- health information exchange
integrations:
- Malaffi
- ADHDS
- ADHDS Malaffi
- ADHDS PHR
- Abu Dhabi Health Data Services
---

# ADHDS Malaffi Integration

## Overview
Abu Dhabi Health Data Services' health information exchange (HIE) platform that connects healthcare providers across Abu Dhabi.

## Features
- Secure sharing of patient health records
- Connection between hospitals, clinics, and healthcare facilities
- Improved care coordination
- Clinical decision-making support

## API Endpoint
https://services.malaffi.ae/v1

## Integration Type
External REST API

## Data Types
- Appointments data
- Patient Health Records (PHR)

## ADHDS PHR (Patient Health Records)
Patient-controlled digital health record system managed by Abu Dhabi Health Data Services. Allows individuals to:
- Access personal health information
- Manage health records
- Share health data with providers
- View medical history, test results, appointments, and medications

## Usage in Sahatna
- PHR Service Module: Retrieves Patient Health Records
- Integration Service Module: Appointment data exchange
- Patient Service Module: Survey triggers on health events

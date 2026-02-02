---
doc_id: sahatna-integration-service
component_name: Integration Service
component_type: api
is_internal: true
document_type: service-architecture
project: Sahatna Super App
service: Integration Service
port: 8107
health_endpoint: /integration/actuator/health
internal_systems:
- Integration Service
- Integration Service Module
capabilities:
- FHIR transformation
- data validation
- provider integration
- EHR integration
- EMR integration
- token validation
- signature verification
integrations:
- Okadoc
- Malaffi
- FHIR
- EHR
- EMR
- Appointment Service
- Provider Service
---

# Integration Service Module

## Overview
Application component developed in Java, deployed in Docker container format within Kubernetes cluster. Works closely with Appointment Service Module.

## Main Features
- REST-based Service backing communication between Sahatna Super App backend and:
  - EHR aggregator (Okadoc)
  - HIE (Malaffi)
  - Facility's EHR/EMR within Appointment arrangement workflow
- Validation and transformation of incoming data in FHIR/JSON format into internal Sahatna Super App data format
- Validation of provider requests (signature check of provider tokens by public key)
- Handling/routing connections between Super App backend and provider information systems

## Technical Specifications
- **Deployment**: Container Image / Jar
- **Language**: Java
- **Port**: 8107
- **Health Endpoint**: /integration/actuator/health
- **Communication**: REST/HTTP, gRPC
- **Data Persistence**: Redis (Cache Instance), Redis (Pub/Sub Instance)

## Data Handling
- NOT backed by MS SQL or MongoDB for persistence
- Uses Azure Redis Cache Instance to temporarily store provider state data (base URL, custom headers, etc.)

## Dependencies
- Appointment Service Module
- Provider Service Module
- External: Providers (EHR/EMR systems), Okadoc, Malaffi

## Component Dependencies
- Azure: API Gateway, NAT Gateway
- External: Mobile App (iOS, Android), Providers
- Database: Azure MS SQL, Azure MongoDB, Redis (Cache), Redis (Pub/Sub)

## FHIR Integration
FHIR (Fast Healthcare Interoperability Resources) is the healthcare data interchange format used for communication with external EHR/EMR systems and HIE platforms.

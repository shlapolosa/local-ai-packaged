---
doc_id: sahatna-phr-service
component_name: PHR Service
component_type: api
is_internal: true
document_type: service-architecture
project: Sahatna Super App
service: PHR Service
port: 8100
health_endpoint: /phr/actuator/health
internal_systems:
- PHR Service
- PHR Service Module
- Patient Health Records
capabilities:
- health records
- PHR
- patient health records
- HIE access
- Malaffi integration
- emirates ID validation
integrations:
- Malaffi
- ADHDS
- Patient Service
---

# PHR Service Module (Patient Health Records)

## Overview
Application component developed in Java, deployed in Docker container format within Kubernetes cluster.

## Main Features
- Getting Patient Health Records from HIE database handled by Malaffi (https://services.malaffi.ae/v1)
- Validation of emirates_id against Patient Service Module
- Works with sensitive personal data obtained from Malaffi DB

## Technical Specifications
- **Deployment**: Container Image / Jar
- **Language**: Java
- **Port**: 8100
- **Health Endpoint**: /phr/actuator/health
- **Communication**: REST/HTTP, gRPC
- **Data Persistence**: N/A (no MS SQL or MongoDB - uses Redis Cache only)

## Data Handling
- PHR Service Module is NOT backed by MS SQL or MongoDB for data persistence because it works with sensitive personal data obtained from Malaffi DB
- Uses Azure Redis Cache Instance only for temporary safe patient data storage in JSON format

## Dependencies
- Patient Service Module
- Malaffi Service (external)

## Component Dependencies
- Azure: API Gateway, NAT Gateway
- External: Mobile App (iOS, Android), Malaffi Service
- Database: Redis (Cache Instance) - temporary storage only

## About Malaffi
ADHDS Malaffi System is Abu Dhabi Health Data Services' health information exchange platform that connects healthcare providers across Abu Dhabi. Malaffi enables secure sharing of patient health records between hospitals, clinics, and healthcare facilities to improve care coordination and clinical decision-making.

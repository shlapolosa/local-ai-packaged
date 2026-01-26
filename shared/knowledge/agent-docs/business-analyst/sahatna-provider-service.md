---
doc_id: sahatna-provider-service
scope:
  internalSystems:
  - Provider Service
  - Provider Service Module
  - provider_dbo
  - Provider Portal
  internalCapabilities:
  - license validation
  - physician management
  - facility management
  - provider data sync
  - DOH synchronization
  supportedIntegrations:
  - DOH
  - Notification Service
  - Reference Service
  - Appointment Service
  - Batch-worker Service
documentType: service-architecture
project: Sahatna Super App
service: Provider Service
---

# Provider Service Module

## Overview
Application component developed in Java, deployed in Docker container format within Kubernetes cluster.

## Main Features
- Validation of License ID of Physicians and Facilities against DOH database
- Physicians and facilities data management within Provider Portal web application
- Daily basis synchronization with DOH database within batch-worker service module

## Technical Specifications
- **Deployment**: Container / Jar
- **Language**: Java
- **Port**: 8092
- **Health Endpoint**: /provider/actuator/health
- **Communication**: REST/HTTP, gRPC
- **Data Persistence**: Azure MS SQL

## Database Schema: provider_dbo
- administrator, admins_status_history
- facility, doh_facility, facility_type
- facility_associated_to_provider_admin
- facility_payment_method, payment_method
- facility_physician, facility_speciality_association
- physician, doh_physician, doh_history
- speciality, sub_speciality
- education, experience, language, physician_language
- favourite_physician
- working_day
- invitation_link, custom_header
- flyway_schema_history

## Dependencies
- Notification Service Module
- Reference Service Module
- Appointment Service Module
- Batch-worker Service Module
- External: DOH DB

## Component Dependencies
- Azure: API Gateway, NAT Gateway, WAF (Web Application Firewall), Object Storage
- External: Mobile App (iOS, Android), Web Application (Provider Portal), DOH DB
- Database: MS SQL, Redis (Pub/Sub), Redis (Cache)
- K8s: etcd DB (secrets storage)

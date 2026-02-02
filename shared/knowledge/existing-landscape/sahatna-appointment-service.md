---
doc_id: sahatna-appointment-service
component_name: Appointment Service
component_type: api
is_internal: true
document_type: service-architecture
project: Sahatna Super App
service: Appointment Service
port: 8094
health_endpoint: /appointment/actuator/health
database_schema: appointment_dbo
internal_systems:
- Appointment Service
- Appointment Service Module
- appointment_dbo
- schedules collection
- slots collection
capabilities:
- appointment booking
- appointment creation
- appointment cancellation
- appointment rescheduling
- schedule management
- slot management
integrations:
- Integration Service
- Provider Service
- EHR
- EMR
---

# Appointment Service Module

## Overview
Application component developed in Java, deployed in Docker container format within Kubernetes cluster. Works closely with Integration Service Module.

## Main Features
- Handling Patient Appointment lifecycle:
  - Create appointments
  - Update appointments (rescheduling)
  - Cancel appointments (delete)
- Synchronization with source of Appointment data:
  - Aggregator EHR/EMR DB
  - Facilities EHR/EMR DB
- Providing all appointments to user (view all appointments)

## Technical Specifications
- **Deployment**: Container Image / Jar
- **Language**: Java
- **Port**: 8094
- **Health Endpoint**: /appointment/actuator/health
- **Communication**: REST/HTTP, gRPC
- **Data Persistence**: Azure MS SQL, Azure MongoDB (Cosmos DB)

## Database Schema: appointment_dbo (MS SQL)
- appointment, appointment_history
- appointment_type, service_type
- slot_associated_to_appointment, new_slot_associated_to_appointment
- flyway_schema_history

## MongoDB Collections (Cosmos DB)
- schedules collection
- slots collection

## Dependencies
- Integration Service Module
- Provider Service Module

## Key Workflows
1. Appointment Creation (from Mobile App)
2. Appointment Cancellation (sync mode from Mobile App)
3. Appointment Rescheduling (sync mode from Mobile App)

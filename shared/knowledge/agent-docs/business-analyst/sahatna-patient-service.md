---
doc_id: sahatna-patient-service
scope:
  internalSystems:
  - Patient Service
  - Patient Service Module
  - patient_dbo
  internalCapabilities:
  - patient information
  - personal data
  - communication preferences
  - feedback management
  - surveys
  - dependants management
  supportedIntegrations:
  - DOH
  - MOI
  - UAE Pass
  - Malaffi
  - Notification Service
  - Reference Service
  - Appointment Service
  - PHR Service
documentType: service-architecture
project: Sahatna Super App
service: Patient Service
---

# Patient Service Module

## Overview
Application component developed in Java, deployed in Docker container format within Kubernetes cluster.

## Main Features
- Getting personal patient information from DOH via SOAP API (DOH has internal integration with MOI database)
- Managing patient's Communication Preferences (SMS/Email/Push)
- Managing feedback: pop-up with title, questions, star ratings, free input text for user experience rating
- Managing Surveys: triggered by Malaffi upon health-related actions (encounter, laboratory test)
  - Sending survey notifications per preferred notification preference
  - Processing and persisting survey questions/answers for DOH Data Analytics team

## Technical Specifications
- **Deployment**: Container
- **Language**: Java
- **Port**: 8091
- **Health Endpoint**: /patient/actuator/health
- **Communication**: REST/HTTP, gRPC
- **Data Persistence**: Azure MS SQL

## Database Schema: patient_dbo
- patient, deleted_patient, pilot_patient
- device, patient_associated_to_device
- location
- notification_preferences
- feedback, feedback_question
- otp, password_history, temp_locked_user
- dependant_associated_to_guardian, shared_accounts_association, unlink_dependant_history
- phc_details, phc_history, phc_notification_delivery, phc_reason
- support, deletion_reason
- flyway_schema_history

## Dependencies
- Notification Service Module
- Reference Service Module
- Appointment Service Module
- PHR Service Module
- External: UAE PASS DB, MOI DB (via DOH Integration Hub)

## Component Dependencies
- Azure: API Gateway, NAT Gateway
- Database: MS SQL, Redis (Pub/Sub), Redis (Cache)
- K8s: etcd DB (secrets storage)

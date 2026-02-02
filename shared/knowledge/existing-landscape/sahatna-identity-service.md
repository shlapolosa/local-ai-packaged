---
doc_id: sahatna-identity-service
component_name: Identity Service
component_type: api
is_internal: true
document_type: service-architecture
project: Sahatna Super App
service: Identity Service
port: 8090
health_endpoint: /identity/actuator/health
database_schema: identity_dbo
internal_systems:
- Identity Service
- Identity Service Module
- identity_dbo
capabilities:
- authentication
- login
- logout
- token management
- UAE Pass login
- guest login
- language preference
integrations:
- UAE Pass
- Notification Service
---

# Identity Service Module

## Overview
Application component developed in Java, deployed in Docker container format within Kubernetes cluster.

## Main Features
- [Patient] Login Using UAE Pass
- [Guest] Login - Anonymously
- [Patient] Logout Using UAE Pass
- Token Management: issuing, encryption and validation of security tokens for securing communication between Mobile App and backend services
- Language Preference (En/Ar)

## Technical Specifications
- **Deployment**: Container Image / K8s
- **Language**: Java 17
- **Port**: 8090
- **Health Endpoint**: /identity/actuator/health
- **Communication**: REST/HTTP, gRPC
- **Data Persistence**: Azure MS SQL
- **Source Code**: https://bitbucket.org/injazat-workspace/identity-service/src/main/

## Database Schema: identity_dbo
- password_history
- temp_locked_user
- token
- otp
- flyway_schema_history

## Dependencies
- Notification Service Module
- UAE Pass (external)

## Functional Scope
- FR-001-001: Patient Login Using UAE Pass (UaePassMobileController)
- FR-001-002: Guest Login Using UAE Pass (GuestAuthMobileController)
- FR-001-003: Patient Logout
- FR-001-004: Token Management
- FR-001-005: Language Preference

## Component Dependencies
- Azure: API Gateway, NAT Gateway
- External: UAE PASS
- Internal: Notification Service Module
- Database: MS SQL, Redis (Pub/Sub), Redis (Cache)
- K8s: etcd DB (secrets storage)

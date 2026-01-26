---
doc_id: sahatna-teleconsultation-service
scope:
  internalSystems:
  - Teleconsultation Service
  - Teleconsultation Service Module
  - teleconsultation_dbo
  internalCapabilities:
  - video conferencing
  - teleconsultation
  - video calls
  - video recording
  - secure chat
  - telemedicine
  - remote consultation
  supportedIntegrations:
  - Vidyo
  - Vidyo Platform
  - Appointment Service
  - Integration Service
documentType: service-architecture
project: Sahatna Super App
service: Teleconsultation Service
---

# Teleconsultation Service Module

## Overview
Application component developed in Java, deployed in Docker container format within Kubernetes cluster.

## Main Features
- Video conference capability between Patient and Physician
- Video recording of video conferences between Patient and Physician
- Secure chatting between Patient and Physician
- Backed by Vidyo Platform solution for video capabilities

## Technical Specifications
- **Deployment**: Container Image / Jar
- **Language**: Java
- **Port**: 8097
- **Health Endpoint**: /teleconsultation/actuator/health
- **Communication**: REST/HTTP, gRPC
- **Data Persistence**: Azure MS SQL Instance, Azure Redis (Pub/Sub Instance)

## Database Schema: teleconsultation_dbo (MS SQL)
- call, call_session
- record
- feedback
- notification
- physician
- room
- appointment
- patient
- flyway_schema_history

## Dependencies
- Appointment Service Module
- Integration Service Module
- Web Application Teleconsultation Module (Web Page)
- Vidyo Platform (external)

## Component Dependencies
- Azure: API Gateway, NAT Gateway, WAF/ALB
- External: Mobile App (iOS, Android), Providers, Vidyo Platform
- Database: Azure MS SQL, Redis (Cache), Redis (Pub/Sub)

## About Vidyo Platform
A video conferencing and telemedicine platform that enables secure video communications for healthcare consultations, remote patient monitoring, and virtual care delivery. It provides HIPAA-compliant video solutions specifically designed for healthcare environments.

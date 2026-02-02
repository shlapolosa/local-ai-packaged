---
doc_id: sahatna-notification-service
component_name: Notification Service
component_type: api
is_internal: true
document_type: service-architecture
project: Sahatna Super App
service: Notification Service
port: 8104
health_endpoint: /notification/actuator/health
internal_systems:
- Notification Service
- Notification Service Module
- templates collection
capabilities:
- notifications
- email notifications
- SMS notifications
- push notifications
- notification templates
- SMTP
- Firebase
integrations:
- Firebase
- SMS Global
- SMTP
- Relay SMTP
- Google Firebase
---

# Notification Service Module

## Overview
Application component developed in Java, deployed in Docker container format within Kubernetes cluster.

## Main Features
- Notification of events happening within patient data processing workflow
- Three communication channels for patient notifications:
  1. Relay SMTP Server (email)
  2. SMS Global Service (SMS)
  3. Google Firebase (push notifications)
- Template management of notification messages within Provider Portal web application

## Technical Specifications
- **Deployment**: Container Images / Jar
- **Language**: Java
- **Port**: 8104
- **Health Endpoint**: /notification/actuator/health
- **Communication**: REST/HTTP, gRPC
- **Data Persistence**: Azure Cosmos DB

## MongoDB Collections
- templates collection containing JSON notification templates

## Dependencies
- External Systems: SMS Gateway, Email Gateway, Push notification provider
- All other Super App Service Modules

## Component Dependencies
- Azure: API Gateway, NAT Gateway
- External: Mobile App (iOS, Android), Provider Portal (Web Application)
- External Services: Firebase (PUSH), Relay SMTP (email), Global SMS (SMS)
- Database: Azure MongoDB (Cosmos DB), Redis (Pub/Sub Instance)

## Notification Channels
- **Firebase**: Google's platform for push notifications to mobile devices
- **SMS Global**: Third-party SMS gateway service
- **Relay SMTP**: Email server for sending email notifications

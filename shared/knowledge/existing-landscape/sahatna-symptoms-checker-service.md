---
doc_id: sahatna-symptoms-checker-service
component_name: Symptoms-Checker Service
component_type: api
is_internal: true
document_type: service-architecture
project: Sahatna Super App
service: Symptoms-Checker Service
port: 8095
health_endpoint: /symptomschecker/actuator/health
internal_systems:
- Symptoms-Checker Service
- Symptoms-Checker Service Module
- symptoms collection
capabilities:
- symptom checking
- symptom analysis
- AI diagnosis
- clinical decision support
integrations:
- Isabella Service
- Isabella
- Batch-worker Service
---

# Symptoms-Checker Service Module

## Overview
Application component developed in Java, deployed in Docker container format within Kubernetes cluster.

## Main Features
- Checking symptoms data provided by patients against Isabella Service database (https://arscstsandbox.isabelhealthcare.com/)
- AI-powered symptom analysis and diagnosis suggestions

## Technical Specifications
- **Deployment**: Container / Jar
- **Language**: Java
- **Port**: 8095
- **Health Endpoint**: /symptomschecker/actuator/health
- **Communication**: REST/HTTP, gRPC
- **Data Persistence**: Azure MongoDB (Cosmos DB)

## MongoDB Collections
- symptoms collection containing:
  - ageGroup
  - country
  - pregnancy
  - predictivetexts

## Dependencies
- Isabella Service (external)
- Batch-worker Service Module

## Component Dependencies
- Azure: API Gateway, NAT Gateway
- External: Mobile App (iOS, Android), Isabella Service
- Database: Azure MongoDB (Cosmos DB), Redis (Cache)

## About Isabella Service
Isabella is an AI-powered clinical decision support system and symptom checker used by healthcare professionals worldwide since 2001. It analyzes multiple symptoms simultaneously to suggest potential diagnoses for both common and rare conditions, helping reduce diagnostic errors and improve patient safety through advanced artificial intelligence algorithms.

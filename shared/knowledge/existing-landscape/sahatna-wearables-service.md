---
doc_id: sahatna-wearables-service
component_name: Wearables Service
component_type: api
is_internal: true
document_type: service-architecture
project: Sahatna Super App
service: Wearables Service
port: 8111
health_endpoint: /wearables/actuator/health
internal_systems:
- Wearables Service
- Wearables Service Module
capabilities:
- wearables
- wellness tracking
- steps tracking
- nutrition tracking
- sleep tracking
- heart rate monitoring
- smart goals
- health data sync
integrations:
- Apple Health
- Apple HealthKit
- HealthKit
- Google Fit
- Health Connect
- Fractal AI
- Patient Service
---

# Wearables Service Module

## Overview
Application component developed in Java, deployed in Docker container format within Kubernetes cluster.

## Main Features
- Integration with native aggregators:
  - Apple HealthKit (iOS)
  - Google Fit / Health Connect (Android)
- Tracking wellness data: steps, nutrition, sleep, heart rate
- Smart Goals incorporation via Fractal AI integration

## Technical Specifications
- **Deployment**: Container Image / Jar
- **Language**: Java
- **Port**: 8111
- **Health Endpoint**: /wearables/actuator/health
- **Communication**: REST/HTTP, gRPC
- **Data Persistence**: Azure Cosmos DB Instance, Azure Redis (Pub/Sub Instance)

## Dependencies
- Patient Service Module
- Fractal AI (external system)

## Fractal AI Integration
Fractal AI analyzes patient health insights (vital signs) using fractal algorithms and mathematical models to set/predicate 'steps' smart goals based on historical data.

## Design Decisions

### 1. Limited Data Sync Points (24 per day)
- Higher granularity requires significant bandwidth increase
- For 300K users at 5% daily active (15K DAU):
  - Hourly sync: 4.167 QPS
  - Minute sync: 250 QPS (60x increase)
- Service scaling cost not justified by business value

### 2. Foreground Sync Only (No Background)
- Background sync requires elevated user permissions
- System limitations affect background data delivery:
  - Disabled Background App Refresh
  - Focus mode or power-intensive app restrictions
  - Low battery or power-saving mode blocks HealthKit updates
- Background processing increases power consumption
- Impacts user experience negatively

## Data Storage
- Cosmos DB: Wellness data storage
- Redis: Temporary dependent info caching (ID, EID, list of dependents)

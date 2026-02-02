---
doc_id: sahatna-technology-stack
component_name: sahatna-technology-stack
component_type: infrastructure
is_internal: true
document_type: technology-stack
project: Sahatna Super App
internal_systems:
- Azure SQL
- Cosmos DB
- Redis
- Kubernetes
- Dapr
- API Gateway
- KeyVault
- Azure Monitor
- etcd
- WAF
capabilities:
- database
- caching
- container orchestration
- service mesh
- API management
- secrets management
- monitoring
- logging
- security
integrations:
- Microsoft Azure
- Oracle API Gateway
- Strapi
---

# Sahatna Technology Stack

## Cloud Platform
- Microsoft Azure

## Container Orchestration
- Kubernetes
- Dapr (Sidecar pattern implementation)

## API Management
- Oracle API Gateway 11g
- Azure API Gateway
- NAT Gateway

## Programming Languages & Frameworks
- **Backend**: Java 17 + Spring Boot + Dapr
- **Frontend Web**: React JS
- **Frontend Mobile**: React Native

## Databases & Storage
- Azure SQL (MSSQL) - Structured data
- Cosmos DB (MongoDB) - Document database for unstructured data
- Azure Cache for Redis - In-memory caching and Pub/Sub
- Azure Object Storage - File storage
- Log Analytics Workspace - Log management

## Content Management
- Strapi CMS - Headless CMS for dynamic mobile content

## Configuration Management
- K8s ConfigMap & Secrets (backed by Azure KeyVault)
- etcd DB (secrets storage in Kubernetes)

## Security
- WAF (Web Application Firewall)
- Azure KeyVault

## Communication Protocols
- REST/HTTP - Primary API protocol
- gRPC - Inter-service communication
- FHIR/JSON - Healthcare data interchange
- SOAP - Legacy DOH integrations

---
doc_id: sahatna-sidecar-pattern
scope:
  internalSystems:
  - Dapr
  - Kubernetes
  internalCapabilities:
  - sidecar pattern
  - service mesh
  - service communication
  - reverse proxy
  supportedIntegrations: []
documentType: architecture-pattern
project: Sahatna Super App
---

# Sidecar Pattern (Dapr Implementation)

## Overview
Sidecar is a reverse proxy component that runs beside the application and facilitates communication with other services or the outside world.

## Implementation in Sahatna
- Dapr is used as the sidecar technology
- Both containers run side by side in the same Kubernetes cluster
- Scale individually

## Benefits
- **Language Independence**: Sidecar is independent from primary application's runtime environment and programming language
- **Resource Access**: Sidecar can access same resources as primary application, can monitor system resources
- **Low Latency**: Proximity to primary application means no significant communication latency
- **Extensibility**: Can extend functionality even for applications without extensibility mechanisms

## Deployment
- Components deployed as separate process or container
- Provides isolation and encapsulation
- Enables heterogeneous components and technologies
- Shares lifecycle with parent application

## Service-to-Service Communication
Dapr handles service-to-service communication within the sidecar template, managing:
- Service discovery
- Request routing
- Load balancing
- Retries and circuit breaking

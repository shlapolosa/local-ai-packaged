---
doc_id: sahatna-health-checks
component_name: sahatna-health-checks
component_type: operations
is_internal: true
document_type: operations
project: Sahatna Super App
internal_systems:
- Dapr
- Kubernetes
capabilities:
- health checks
- monitoring
- probes
- actuator
---

# Sahatna Application Health Checks

## Overview
Applications can become unresponsive due to:
- Being too busy to accept new work
- Crashes
- Deadlock states

Dapr provides capability for monitoring app health through probes.

## Health Endpoints by Service

| Service | Port | Health Endpoint |
|---------|------|----------------|
| Identity Service | 8090 | /identity/actuator/health |
| Patient Service | 8091 | /patient/actuator/health |
| Provider Service | 8092 | /provider/actuator/health |
| Appointment Service | 8094 | /appointment/actuator/health |
| Symptoms-Checker | 8095 | /symptomschecker/actuator/health |
| Teleconsultation | 8097 | /teleconsultation/actuator/health |
| PHR Service | 8100 | /phr/actuator/health |
| Notification Service | 8104 | /notification/actuator/health |
| Integration Service | 8107 | /integration/actuator/health |
| Wearables Service | 8111 | /wearables/actuator/health |

## Dapr Health Monitoring
- Detects unresponsive applications
- Stops accepting new work for unhealthy apps
- Reacts to status changes automatically

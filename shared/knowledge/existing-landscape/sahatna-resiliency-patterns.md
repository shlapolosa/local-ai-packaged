---
doc_id: sahatna-resiliency-patterns
component_name: sahatna-resiliency-patterns
component_type: pattern
is_internal: true
document_type: architecture-pattern
project: Sahatna Super App
internal_systems:
- Dapr
capabilities:
- resiliency
- fault tolerance
- circuit breaker
- retries
- timeouts
- error handling
---

# Sahatna Resiliency Patterns

## Overview
Distributed applications with many microservices face potential system failures. Dapr provides fault tolerance resiliency policies.

## Timeout Pattern
Configurable timeouts for all service calls to prevent indefinite waiting.

## Retry Pattern with Back-off
Handles transient failures in cloud environments:

### Retry Strategies
1. **Cancel**: For non-recoverable errors (e.g., invalid credentials) - don't retry
2. **Retry Immediately**: For rare/unusual failures (e.g., corrupted network packets) - retry same request
3. **Retry After Delay**: For connectivity or busy failures - wait suitable time before retry

### Transient Faults
- Momentary loss of network connectivity
- Temporary service unavailability
- Timeouts when service is busy
- Database throttling under load

## Circuit Breaker Pattern
Handles faults that may take variable time to recover. Prevents cascading failures.

### States
1. **Closed**: Normal operation
   - Routes requests to operation
   - Counts recent failures
   - Switches to Open when threshold exceeded

2. **Open**: Fail-fast mode
   - Returns exception immediately
   - Starts timeout timer
   - Switches to Half-Open when timer expires

3. **Half-Open**: Recovery testing
   - Limited requests allowed through
   - If successful, switches to Closed (failure counter reset)
   - If fails, reverts to Open

### Benefits
- Prevents resource exhaustion (memory, threads, DB connections)
- Allows system time to recover
- Protects against cascading failures
- Prevents flooding recovering services

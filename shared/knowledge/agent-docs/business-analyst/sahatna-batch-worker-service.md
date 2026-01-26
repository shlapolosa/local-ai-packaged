---
doc_id: sahatna-batch-worker-service
scope:
  internalSystems:
  - Batch Worker Service
  - Batch-worker Service
  internalCapabilities:
  - batch processing
  - cron jobs
  - scheduled jobs
  - data synchronization
  - DOH sync
  supportedIntegrations:
  - DOH
  - Provider Service
documentType: service-architecture
project: Sahatna Super App
service: Batch Worker Service
---

# Batch Worker Service

## Overview
Responsible for scheduling and triggering background cron jobs.

## Main Features
- Daily syncing of facilities/physicians data from DOH licensing system
- Scheduled background job execution
- Cron job management

## Key Jobs
- Daily facilities data sync from DOH
- Daily physicians data sync from DOH

## Dependencies
- Provider Service Module
- DOH Licenses Info System (external)

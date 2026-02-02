---
doc_id: sahatna-batch-worker-service
component_name: Batch Worker Service
component_type: api
is_internal: true
document_type: service-architecture
project: Sahatna Super App
service: Batch Worker Service
internal_systems:
- Batch Worker Service
- Batch-worker Service
capabilities:
- batch processing
- cron jobs
- scheduled jobs
- data synchronization
- DOH sync
integrations:
- DOH
- Provider Service
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

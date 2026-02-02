---
doc_id: sahatna-reference-service
component_name: Reference Service
component_type: api
is_internal: true
document_type: service-architecture
project: Sahatna Super App
service: Reference Service
database_schema: reference_data_dbo
internal_systems:
- Reference Service
- Reference Data Service
- reference_data_dbo
capabilities:
- reference data
- lookup values
- FAQs
- country lists
- document types
---

# Reference Data Service Module

## Overview
Responsible for providing lookup values for Sahatna mobile app.

## Main Features
- FAQs
- Country lists
- State/city lists
- Document types
- Reasons
- Mobile language support

## Database Schema: reference_data_dbo (MS SQL)
- country, state, city
- faq, faq_topic
- document_type
- mobile_language
- reason
- flyway_schema_history

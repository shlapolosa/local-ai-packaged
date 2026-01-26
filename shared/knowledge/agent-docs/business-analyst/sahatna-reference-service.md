---
doc_id: sahatna-reference-service
scope:
  internalSystems:
  - Reference Service
  - Reference Data Service
  - reference_data_dbo
  internalCapabilities:
  - reference data
  - lookup values
  - FAQs
  - country lists
  - document types
  supportedIntegrations: []
documentType: service-architecture
project: Sahatna Super App
service: Reference Service
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

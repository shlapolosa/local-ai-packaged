---
doc_id: sahatna-payment-service
component_name: Payment Service
component_type: api
is_internal: true
document_type: service-architecture
project: Sahatna Super App
service: Payment Service
internal_systems:
- Payment Service
capabilities:
- payment processing
- payments
- teleconsultation payments
integrations:
- ADPay
- Abu Dhabi Payment Gateway
---

# Payment Service

## Overview
Responsible for handling payment features for patients.

## Main Features
- Payment processing for teleconsultation services
- Integration with ADPay (Abu Dhabi Payment Gateway)

## ADPay Integration
ADPay is the Abu Dhabi payment gateway used for processing payments within the Sahatna Super App, particularly for teleconsultation services.

## Data Source
- ADPay: External REST API integration
- Type: Payment gateway

---
doc_id: sahatna-payment-service
scope:
  internalSystems:
  - Payment Service
  internalCapabilities:
  - payment processing
  - payments
  - teleconsultation payments
  supportedIntegrations:
  - ADPay
  - Abu Dhabi Payment Gateway
documentType: service-architecture
project: Sahatna Super App
service: Payment Service
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

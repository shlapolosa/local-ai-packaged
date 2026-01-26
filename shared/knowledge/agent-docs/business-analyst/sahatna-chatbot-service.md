---
doc_id: sahatna-chatbot-service
scope:
  internalSystems:
  - Chatbot Service
  internalCapabilities:
  - chatbot
  - AI chatbot
  - LLM integration
  - conversational AI
  supportedIntegrations:
  - M42
  - Med42
  - Patient LLM
documentType: service-architecture
project: Sahatna Super App
service: Chatbot Service
---

# Chatbot Service

## Overview
Responsible for handling requests/responses from M42 patient LLM and providing the required format for the frontend.

## Main Features
- Integration with M42 Patient LLM (Med42)
- Request/response handling for AI chatbot functionality
- Formatting responses for mobile frontend

## M42 Patient LLM (Med42)
Designed to transform AI applications in healthcare and improve patient care outcomes. Med42 LLM acts as the backbone for Sahatna's AI Chatbot module.

## Data Source
- M42: External REST API
- Purpose: LLM for chatbot functionality

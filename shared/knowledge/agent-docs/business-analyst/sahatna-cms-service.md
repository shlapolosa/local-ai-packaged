---
doc_id: sahatna-cms-service
scope:
  internalSystems:
  - CMS Service
  internalCapabilities:
  - content management
  - CMS
  - media content
  - news
  - articles
  - events
  supportedIntegrations:
  - Strapi
  - Strapi CMS
  - AD360
documentType: service-architecture
project: Sahatna Super App
service: CMS Service
---

# CMS Service

## Overview
Acts as a wrapper layer exposing APIs to allow 3rd parties to push media content to Sahatna's CMS.

## Main Features
- API wrapper for Strapi CMS
- Allows AD360 to push media content
- Content types: news, articles, events, etc.
- Content rendered on Sahatna mobile app

## Strapi CMS
An open-source headless content management system that provides APIs for managing and delivering digital content. It allows developers to create, manage, and distribute content across multiple channels and applications through customizable APIs and administrative interfaces.

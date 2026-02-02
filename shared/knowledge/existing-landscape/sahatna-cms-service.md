---
doc_id: sahatna-cms-service
component_name: CMS Service
component_type: api
is_internal: true
document_type: service-architecture
project: Sahatna Super App
service: CMS Service
internal_systems:
- CMS Service
capabilities:
- content management
- CMS
- media content
- news
- articles
- events
integrations:
- Strapi
- Strapi CMS
- AD360
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

# Healthcare Application Reference Architecture

Source: Enterprise Architecture Standards for Healthcare Providers

## Overview

This reference architecture defines the standard layered architecture for healthcare applications. It guides the generation of ArchiMate Application Layer elements.

## Architecture Layers

### Layer 1: Presentation Layer
**Purpose**: User interfaces for patients, providers, and staff

| Component | ID Pattern | Description |
|-----------|------------|-------------|
| Mobile Application | `id-ac-mobile` | Native/hybrid mobile app for patients |
| Web Portal | `id-ac-web` | Browser-based interface for all users |
| Provider Portal | `id-ac-provider-portal` | Clinician-facing web interface |
| Admin Console | `id-ac-admin` | Administrative interface |

**ArchiMate Elements**:
- ApplicationComponent for each UI
- ApplicationInterface for each component's API

### Layer 2: Gateway Layer
**Purpose**: Security perimeter, routing, rate limiting, API management

| Component | ID Pattern | Description |
|-----------|------------|-------------|
| Firewall | `id-ac-firewall` | Network security (optional in diagram) |
| API Gateway | `id-ac-gateway` | Central API routing and management |
| Load Balancer | `id-ac-lb` | Traffic distribution |

**ArchiMate Elements**:
- ApplicationComponent for gateway
- ApplicationInterface for public APIs
- ApplicationFunction for routing, rate-limiting

### Layer 3: Identity & Access Management (IAM)
**Purpose**: Authentication, authorization, SSO, user management

| Component | ID Pattern | Description |
|-----------|------------|-------------|
| Identity Provider | `id-ac-identity` | Authentication service |
| Authorization Service | `id-ac-authz` | RBAC/ABAC policy enforcement |
| Session Manager | `id-ac-session` | Token/session management |

**ArchiMate Elements**:
- ApplicationComponent for IAM
- ApplicationService for auth/authz capabilities
- ApplicationFunction for token validation, policy evaluation

### Layer 4: Service Layer (Bounded Contexts)
**Purpose**: Business logic organized by domain

| Domain | ID Pattern | Description |
|--------|------------|-------------|
| Patient Domain | `id-ac-patient` | Patient demographics, preferences |
| Provider Domain | `id-ac-provider` | Clinician profiles, schedules |
| Appointment Domain | `id-ac-appointment` | Scheduling, booking |
| Clinical Domain | `id-ac-clinical` | Medical records, notes |
| Notification Domain | `id-ac-notification` | Alerts, reminders, communications |
| Billing Domain | `id-ac-billing` | Claims, payments |
| Eligibility Domain | `id-ac-eligibility` | Insurance verification |
| Screening Domain | `id-ac-screening` | Preventive health programs |

**ArchiMate Elements**:
- ApplicationComponent per domain
- ApplicationService for exposed capabilities
- ApplicationInterface for domain APIs
- ApplicationFunction for business logic
- DataObject for domain entities

### Layer 5: Integration/ESB Layer
**Purpose**: Protocol translation, data mapping, orchestration between internal and external systems

| Component | ID Pattern | Description |
|-----------|------------|-------------|
| Integration Hub | `id-ac-integration` | Central ESB/iPaaS |
| Adapter (per external) | `id-ai-{ext}-adapter` | Protocol adapters |

**Layout Rule**: ESB layer is HORIZONTAL, spanning full width between Service and External layers.

**ArchiMate Elements**:
- ApplicationComponent for integration hub
- ApplicationInterface for each adapter
- ApplicationFunction for transformations

### Layer 6: External Systems Layer
**Purpose**: Third-party and backend provider systems

| System Type | ID Pattern | Examples |
|-------------|------------|----------|
| Health Information Exchange | `id-ac-ext-hie` | Malaffi, CommonWell |
| Insurance/Payer | `id-ac-ext-insurer` | Daman, insurance APIs |
| EMR/EHR Systems | `id-ac-ext-emr` | Epic, Cerner |
| Licensing/Regulatory | `id-ac-ext-licensing` | Accela, DOH systems |
| Lab Systems | `id-ac-ext-lab` | Laboratory information systems |
| Pharmacy Systems | `id-ac-ext-pharmacy` | Prescription networks |

**ArchiMate Elements**:
- ApplicationComponent (external) for each system
- ApplicationInterface for integration points

### Layer 7: Data & Analytics Layer (Future/Optional)
**Purpose**: Reporting, insights, machine learning

| Component | ID Pattern | Description |
|-----------|------------|-------------|
| ELT/CDC Pipelines | `id-ac-etl` | Data ingestion |
| Data Warehouse | `id-ac-dw` | Analytical storage |
| Analytics Engine | `id-ac-analytics` | BI/reporting |
| ML Models | `id-ac-ml` | Predictive models |

## View Layout Guidelines

### Application Architecture View (id-view-application)

```
Y Position   Layer Content
---------    -------------
y=0          PRESENTATION: Mobile, Web Portal (side by side)
y=120        GATEWAY: API Gateway (centered)
y=240        IAM: Identity & Access Management (full width)
y=360        SERVICE: Domain components (side by side)
y=600        ESB: Integration Layer (horizontal, full width)
y=720        EXTERNAL: Backend systems (side by side)
```

### Spacing Rules
- Row spacing: 120px vertical gap between layers
- Column spacing: 200px horizontal gap between components
- Node sizes:
  - Components: 180x60
  - Interfaces: 180x45
  - Functions: 85x40
  - Groupings: 100% width of contained elements + 40px padding

## Relationship Patterns

### Gateway Pattern
- Mobile/Web → Gateway Interface (NOT directly to Gateway Component)
- Gateway Interface → Domain Interface
- Use Flow relationships between interfaces

### Domain-to-External Pattern
- Domain Interface → ESB Adapter Interface → External Interface
- Never skip the ESB layer for external integrations

### IAM Pattern
- All authenticated requests flow through IAM
- IAM serves all domain components

## ArchiMate Color Palette

| Layer | Element Type | Color | Hex |
|-------|--------------|-------|-----|
| Application | Component, Function | Light Blue | #B5D3E7 |
| Application | Interface | Light Blue (border) | #9BC4E2 |
| Application | Service | Yellow | #FFFFB5 |
| Application | Data Object | Green | #C9E7B5 |
| Application | Event | Orange | #FFB5B5 |
| External | All external elements | Gray | #D5D5D5 |

## Usage Notes

1. **Not all layers required**: Only include components explicitly mentioned in requirements
2. **Reference guides layout**: Even if components are minimal, follow layer positions
3. **ESB always horizontal**: Integration layer spans full width
4. **Interfaces for flows**: Gateway patterns use Interface-to-Interface relationships

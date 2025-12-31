# Taskmaster PRD Format Specification

This document defines the 7-section PRD format required for optimal Taskmaster parsing.

## Overview

Taskmaster's `parse_prd` tool works best with structured PRDs that follow this format. The more detailed and well-organized the PRD, the better the generated tasks will be.

## Required Sections

### 1. Overview
High-level context about the product.

```markdown
## 1. Overview

### Problem Statement
{What problem does this solve? Be specific about pain points.}

### Target Audience
{Who is this for? Include primary and secondary users.}

### Value Proposition
{Why would users choose this? What's the unique value?}
```

### 2. Core Features
Feature descriptions with implementation context.

```markdown
## 2. Core Features

### Feature 1: {Name}
- **What it does**: {Clear functional description}
- **Why it's important**: {Business value / user benefit}
- **How it works**: {High-level technical approach}

### Feature 2: {Name}
- **What it does**: {Description}
- **Why it's important**: {Value}
- **How it works**: {Approach}

{Continue for all major features...}
```

### 3. User Experience
User-centered design considerations.

```markdown
## 3. User Experience

### User Personas
- **Persona 1: {Name/Role}**
  - Goals: {What they want to achieve}
  - Frustrations: {Current pain points}
  - Context: {When/where they use the product}

- **Persona 2: {Name/Role}**
  - Goals: {Goals}
  - Frustrations: {Pain points}
  - Context: {Usage context}

### User Flows
1. **{Primary Flow Name}**
   - Step 1: {Action}
   - Step 2: {Action}
   - Step 3: {Action}
   - Outcome: {Expected result}

2. **{Secondary Flow Name}**
   - Step 1: {Action}
   - Step 2: {Action}
   - Outcome: {Expected result}

### Design Considerations
- {Key UX principle 1 - e.g., "Mobile-first responsive design"}
- {Key UX principle 2 - e.g., "Accessibility compliance (WCAG 2.1 AA)"}
- {Key UX principle 3}
```

### 4. Technical Architecture
System design and implementation details.

```markdown
## 4. Technical Architecture

### System Components
- **{Component 1}**: {Purpose and responsibilities}
- **{Component 2}**: {Purpose and responsibilities}
- **{Component 3}**: {Purpose and responsibilities}

### Data Structures
- **{Entity 1}**: {Key fields and relationships}
- **{Entity 2}**: {Key fields and relationships}

### APIs
- **{Endpoint 1}**: {Method} - {Purpose}
- **{Endpoint 2}**: {Method} - {Purpose}
- **{Endpoint 3}**: {Method} - {Purpose}

### Infrastructure
- {Hosting/deployment requirement}
- {Database requirement}
- {Caching/performance requirement}
- {Security requirement}
```

### 5. Development Roadmap
Phased delivery without time estimates.

```markdown
## 5. Development Roadmap

### Phase 1: MVP
**Scope:**
- {Core feature 1}
- {Core feature 2}
- {Essential infrastructure}

**Success Criteria:**
- {Measurable outcome 1}
- {Measurable outcome 2}

### Phase 2: Enhancement
**Scope:**
- {Secondary feature 1}
- {Secondary feature 2}
- {Integration improvements}

**Success Criteria:**
- {Measurable outcome 1}
- {Measurable outcome 2}

### Phase 3: Scale
**Scope:**
- {Advanced feature 1}
- {Advanced feature 2}
- {Performance optimization}

**Success Criteria:**
- {Measurable outcome 1}
- {Measurable outcome 2}
```

### 6. Logical Dependency Chain
Task sequencing for Taskmaster to understand dependencies.

```markdown
## 6. Logical Dependency Chain

### Foundation Layer (Build First)
1. **{Task/Feature}** - Required by: {list downstream dependents}
2. **{Task/Feature}** - Required by: {list downstream dependents}
3. **{Task/Feature}** - Required by: {list downstream dependents}

### Core Layer (Build Second)
4. **{Task/Feature}** - Depends on: {list upstream dependencies}
5. **{Task/Feature}** - Depends on: {list upstream dependencies}
6. **{Task/Feature}** - Depends on: {list upstream dependencies}

### Integration Layer (Build Third)
7. **{Task/Feature}** - Depends on: {list upstream dependencies}
8. **{Task/Feature}** - Depends on: {list upstream dependencies}

### Polish Layer (Build Last)
9. **{Task/Feature}** - Depends on: {list upstream dependencies}
10. **{Task/Feature}** - Depends on: {list upstream dependencies}
```

### 7. Appendix
Supporting materials.

```markdown
## 7. Appendix

### Research References
- {Reference 1: Link or citation}
- {Reference 2: Link or citation}

### Technical Specifications
- {Spec 1: Details}
- {Spec 2: Details}

### Glossary
- **{Term 1}**: {Definition}
- **{Term 2}**: {Definition}
```

## Complete Example

```markdown
# Product Requirements Document: Patient Portal

## 1. Overview

### Problem Statement
Healthcare patients struggle to access their medical records, schedule appointments, and communicate with providers. Current systems require multiple phone calls and long wait times, leading to frustration and delayed care.

### Target Audience
- Primary: Patients aged 25-65 who regularly visit healthcare providers
- Secondary: Caregivers managing health for family members
- Tertiary: Healthcare administrators managing patient communications

### Value Proposition
A unified digital platform that gives patients 24/7 access to their health information, enabling self-service appointment scheduling, secure messaging with providers, and real-time access to test results.

## 2. Core Features

### Feature 1: Patient Dashboard
- **What it does**: Displays overview of upcoming appointments, recent test results, and pending actions
- **Why it's important**: Provides single view of patient's health journey, reducing cognitive load
- **How it works**: Aggregates data from EHR system, presents in card-based responsive UI

### Feature 2: Appointment Scheduling
- **What it does**: Allows patients to book, reschedule, or cancel appointments
- **Why it's important**: Eliminates phone tag with scheduling staff, reduces no-shows
- **How it works**: Real-time availability sync with practice management system, automated reminders

### Feature 3: Secure Messaging
- **What it does**: Enables asynchronous communication between patients and care team
- **Why it's important**: Reduces unnecessary visits for simple questions, documents communications
- **How it works**: End-to-end encrypted messages, integration with EHR for clinical context

### Feature 4: Test Results Viewer
- **What it does**: Displays lab results, imaging reports, and clinical notes
- **Why it's important**: Patients can review results before appointments, track trends over time
- **How it works**: Auto-release after provider review period, with explanation tooltips for medical terms

## 3. User Experience

### User Personas
- **Persona 1: Sarah, Busy Professional**
  - Goals: Quick access to health info, minimal time on phone
  - Frustrations: Can't check results without calling, limited office hours
  - Context: Uses mobile during commute, desktop at work

- **Persona 2: Robert, Caregiver**
  - Goals: Manage health for elderly parent, coordinate with siblings
  - Frustrations: No single source of truth, repeated paperwork
  - Context: Needs proxy access, shared family view

### User Flows
1. **Schedule Appointment**
   - Step 1: Select provider and visit type
   - Step 2: Choose from available time slots
   - Step 3: Confirm and receive confirmation
   - Outcome: Appointment booked, added to calendar

2. **View Test Results**
   - Step 1: Receive notification of new results
   - Step 2: Log in and navigate to results
   - Step 3: Review with explanations, save or share
   - Outcome: Patient informed, can prepare questions

### Design Considerations
- Mobile-first responsive design
- WCAG 2.1 AA accessibility compliance
- High contrast mode for vision-impaired users
- Support for screen readers

## 4. Technical Architecture

### System Components
- **Web Frontend**: React SPA with TypeScript
- **Mobile Apps**: React Native for iOS/Android
- **API Gateway**: Node.js/Express with GraphQL
- **Backend Services**: Microservices for auth, scheduling, messaging
- **Data Layer**: PostgreSQL primary, Redis cache

### Data Structures
- **Patient**: id, demographics, preferences, linked providers
- **Appointment**: id, patient_id, provider_id, datetime, type, status
- **Message**: id, thread_id, sender, recipient, content, timestamp
- **TestResult**: id, patient_id, type, values, reference_ranges, status

### APIs
- **GET /patients/{id}/dashboard**: Patient dashboard data
- **POST /appointments**: Create appointment
- **GET /appointments?patientId={id}**: List appointments
- **POST /messages**: Send message
- **GET /results?patientId={id}**: List test results

### Infrastructure
- AWS EKS for container orchestration
- RDS PostgreSQL for persistence
- ElastiCache Redis for session/cache
- CloudFront CDN for static assets
- HIPAA-compliant configuration throughout

## 5. Development Roadmap

### Phase 1: MVP
**Scope:**
- User authentication and profile
- Basic dashboard with appointments
- View-only test results
- Core API infrastructure

**Success Criteria:**
- 1000 patients can log in and view data
- 95% uptime during business hours

### Phase 2: Enhancement
**Scope:**
- Self-service scheduling
- Secure messaging
- Mobile app release
- Notification system

**Success Criteria:**
- 50% reduction in scheduling calls
- 80% message response within 24 hours

### Phase 3: Scale
**Scope:**
- Proxy/caregiver access
- Integration with additional EHR systems
- Advanced analytics dashboard
- Performance optimization for 100k users

**Success Criteria:**
- Support 100k concurrent users
- Sub-200ms API response times

## 6. Logical Dependency Chain

### Foundation Layer (Build First)
1. **Database schema and migrations** - Required by: all backend services
2. **Authentication service** - Required by: all protected endpoints
3. **Patient data service** - Required by: dashboard, results, messaging
4. **API gateway setup** - Required by: frontend integration

### Core Layer (Build Second)
5. **Dashboard API** - Depends on: patient service, auth
6. **Test results service** - Depends on: patient service, database
7. **Frontend authentication flow** - Depends on: auth service, API gateway
8. **Dashboard UI components** - Depends on: dashboard API, auth flow

### Integration Layer (Build Third)
9. **Appointment service** - Depends on: patient service, external PMS integration
10. **Messaging service** - Depends on: patient service, auth, notification service
11. **Scheduling UI** - Depends on: appointment service
12. **Messaging UI** - Depends on: messaging service

### Polish Layer (Build Last)
13. **Mobile app** - Depends on: all APIs stable
14. **Notification service** - Depends on: messaging, appointments
15. **Analytics dashboard** - Depends on: all data services
16. **Performance optimization** - Depends on: all features complete

## 7. Appendix

### Research References
- HIPAA Security Rule requirements
- HL7 FHIR R4 specification
- Apple Human Interface Guidelines
- Material Design 3 guidelines

### Technical Specifications
- Minimum supported browsers: Chrome 90+, Safari 14+, Firefox 88+
- Minimum mobile OS: iOS 14+, Android 10+
- API rate limits: 100 requests/minute per user

### Glossary
- **EHR**: Electronic Health Record
- **PMS**: Practice Management System
- **HIPAA**: Health Insurance Portability and Accountability Act
```

## Best Practices

### For BA Agents
1. **Be specific** - Vague requirements produce vague tasks
2. **Include the "why"** - Helps Taskmaster prioritize
3. **Define dependencies** - Section 6 is critical for ordering
4. **Scope each phase** - Clear boundaries help task generation
5. **Use consistent naming** - Same terms throughout document

### Common Mistakes
- Missing dependency chain (Section 6)
- Vague feature descriptions
- No technical architecture details
- Mixing implementation with requirements
- Omitting success criteria

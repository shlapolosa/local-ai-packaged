# Architecture Overview

This document provides comprehensive architecture details for both the PRD Generation and White-Label Migration platforms.

---

## Table of Contents

1. [High-Level System Architecture](#high-level-system-architecture)
2. [PRD Generation Architecture](#prd-generation-architecture)
3. [White-Label Migration Architecture](#white-label-migration-architecture)
4. [Technology Stack](#technology-stack)
5. [Intent Routing Architecture](#intent-routing-architecture)
6. [Data Flow](#data-flow)
7. [Security Architecture](#security-architecture)

---

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        User Interface                                │
│                   (Chat Interface / Webhooks)                         │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                  Intent Router (LLM-Powered)                         │
│                                                                      │
│  Confidence Threshold: 0.7                                           │
│  Model: qwen2.5:7b-instruct-q4_K_M                                  │
│  Temperature: 0.2 (consistent classification)                        │
└───┬──────────────────┬─────────────────────┬──────────────────┬────┘
    │                  │                     │                  │
    ▼                  ▼                     ▼                  ▼
┌─────────┐    ┌─────────────┐      ┌──────────┐       ┌──────────┐
│ PRD     │    │ E2E         │      │ White-   │       │ Help /   │
│ Gen     │    │ Solution    │      │ Label    │       │ Unknown  │
└─────────┘    └─────────────┘      └──────────┘       └──────────┘
    │                  │                     │                  │
    └──────────────────┴──────┐              │                  │
                              │              │                  │
                              ▼              ▼                  ▼
                    ┌───────────────┐  ┌──────────┐    ┌──────────────┐
                    │   Business    │  │Migration │    │ Clarification│
                    │   Analyst     │  │ Config   │    │   Response   │
                    └───────────────┘  └──────────┘    └──────────────┘
                              │              │
                              ▼              ▼
                    ┌───────────────┐  ┌──────────┐
                    │ PRD Generator │  │ Master   │
                    │ Orchestrator  │  │ Orch.    │
                    └───────────────┘  └──────────┘
```

---

## PRD Generation Architecture

### Overview

Transforms high-level system briefs into production-ready artifacts through a pipeline of 7 expert agents.

### Detailed Flow

```
User Message
    ↓
Intent Router (detects: prd_generation or e2e_solution)
    ↓
Business Analyst (Requirements Gathering)
    │
    ├→ Interactive Chat Session
    ├→ Extract Functional Requirements
    ├→ Identify Non-Functional Requirements
    ├→ Capture Constraints
    └→ Create Project Record
        ↓
    ┌─────────────────────────────────────┐
    │  PRD Generator Orchestrator         │
    │                                     │
    │  1. Load Project & Requirements     │
    │  2. Initialize Shared Context (v1)  │
    │  3. Query Component Catalog         │
    │  4. Call Experts Sequentially       │
    │  5. Merge Context Updates           │
    │  6. Generate Final PRD              │
    │  7. Save PRD & OAM Definitions      │
    └─────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────────────────────┐
│              Expert Consultation Pipeline                 │
│                                                           │
│  Stage 1: Component Catalog Discovery                    │
│  ├→ Query OAM ComponentDefinitions                       │
│  ├→ Build Platform Capability Catalog                    │
│  └→ Initialize Shared Context                            │
│                                                           │
│  Stage 2: Compliance & Risk Assessor                     │
│  ├→ Webhook: /webhook/expert/compliance-risk             │
│  ├→ Temperature: 0.2 (analytical)                        │
│  ├→ Analyzes: Regulations, Threat Modeling, Security     │
│  └→ Context v2: compliance_requirements,                 │
│     business_constraints, identified_risks               │
│                                                           │
│  Stage 3: Business Architect                             │
│  ├→ Webhook: /webhook/expert/business-architect          │
│  ├→ Temperature: 0.3 (creative)                          │
│  ├→ Creates: Capability Maps, Process Flows, ArchiMate   │
│  └→ Context v3: business_constraints, decision_rationale │
│                                                           │
│  Stage 4: Experience Designer                            │
│  ├→ Webhook: /webhook/expert/experience-designer         │
│  ├→ Temperature: 0.3 (creative)                          │
│  ├→ Designs: Service Blueprints, Journeys, Personas      │
│  └→ Context v4: ux_requirements, decision_rationale      │
│                                                           │
│  Stage 5: Technology CTO                                 │
│  ├→ Webhook: /webhook/expert/technology-cto              │
│  ├→ Temperature: 0.2 (strategic)                         │
│  ├→ Max Tokens: 4000                                     │
│  ├→ Decides: Tech Stack, OAM Validation, Build vs Buy    │
│  └→ Context v5: technology_decisions,                    │
│     infrastructure_constraints                           │
│                                                           │
│  Stage 6: Application Architect                          │
│  ├→ Webhook: /webhook/expert/application-architect       │
│  ├→ Temperature: 0.3 (technical)                         │
│  ├→ Max Tokens: 3500                                     │
│  ├→ Designs: Microservices, Event-Driven, API Contracts  │
│  └→ Context v6: architectural_patterns,                  │
│     decision_rationale                                   │
│                                                           │
│  Stage 7: Solution Architect (PRD-to-OAM)                │
│  ├→ Webhook: /webhook/expert/solution-architect          │
│  ├→ Temperature: 0.2 (precise)                           │
│  ├→ Max Tokens: 4000                                     │
│  ├→ Generates:                                           │
│  │   • Standard OAM (portable)                           │
│  │   • Platform-Specific OAM (uses all components)       │
│  └→ Context v7: oam_definitions, decision_rationale      │
│                                                           │
│  Stage 8: Infrastructure Reviewer                        │
│  ├→ Webhook: /webhook/expert/infrastructure-reviewer     │
│  ├→ Temperature: 0.2 (analytical)                        │
│  ├→ Max Tokens: 3500                                     │
│  ├→ Reviews: Cost, NFRs, Security, Observability, DR     │
│  ├→ Returns: approval_status (approved | requires_changes│
│  └→ Context v8: infrastructure_constraints,              │
│     approval_status                                      │
│                                                           │
│  (Optional) Stage 9: DevOps Engineer                     │
│  ├→ Webhook: /webhook/expert/devops-engineer             │
│  ├→ Only triggered for e2e_solution intent               │
│  └→ Implements: CI/CD, Deployment, Infrastructure        │
└──────────────────────────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────────────────────┐
│                    Final Outputs                          │
│                                                           │
│  1. PRD Document (Markdown)                              │
│  2. Standard OAM YAML                                    │
│  3. Platform-Specific OAM YAML                           │
│  4. Audit Trail (Expert Consultations)                   │
│  5. Shared Context (Final Version)                       │
└──────────────────────────────────────────────────────────┘
```

### Expert Communication Pattern

All experts follow this standardized pattern:

```
┌─────────────────────────────────────────┐
│        Expert Workflow Pattern          │
│                                         │
│  1. Receive: project_id, shared_context│
│  2. Log: Start consultation             │
│  3. Analyze: LLM with expert prompt     │
│  4. Update: Shared context with findings│
│  5. Save: New context version           │
│  6. Complete: Log consultation end      │
│  7. Return: Updated context             │
└─────────────────────────────────────────┘
```

---

## White-Label Migration Architecture

### Overview

Migrates React Native applications to native platforms through a stage-based workflow with PR approvals.

### Detailed Flow

```
User Message
    ↓
Intent Router (detects: whitelabel_migration)
    ↓
Configuration Assistant
    │
    ├→ Interactive Setup
    ├→ Source Repository URL
    ├→ Target Platforms (iOS/Android/Web)
    ├→ Branching Strategy
    └→ GitHub PAT
        ↓
Master Orchestrator
    ↓
┌──────────────────────────────────────────────────────────┐
│              Migration Stage Pipeline                     │
│                                                           │
│  Stage 1: Repository Scaffolding                         │
│  ├→ Agent: Repo Analyzer                                 │
│  ├→ Creates: Mono-repo structure                         │
│  ├→ Directories: ios/, android/, web/, shared/           │
│  └→ Output: PR #1 - "Initial mono-repo scaffold"         │
│                                                           │
│  Stage 2: Analysis & Contracts                           │
│  ├→ Agent: Contract Generator                            │
│  ├→ Analyzes: Components, Logic, Data Models, APIs       │
│  ├→ Generates: Platform-agnostic contracts               │
│  └→ Output: PR #2 - "Component contracts and analysis"   │
│                                                           │
│  Stage 3: Code Generation (Parallel)                     │
│  ├→ iOS Transformer                                      │
│  │   ├→ Generates: SwiftUI views, ViewModels, Models     │
│  │   └→ Output: PR #3 - "iOS implementation"             │
│  ├→ Android Transformer                                  │
│  │   ├→ Generates: Jetpack Compose, ViewModels, Models   │
│  │   └→ Output: PR #4 - "Android implementation"         │
│  └→ Web Transformer                                      │
│      ├→ Generates: React components, Hooks, TypeScript   │
│      └→ Output: PR #5 - "Web implementation"             │
│                                                           │
│  Stage 4: Validation                                     │
│  ├→ Agent: Validator                                     │
│  ├→ Validates: Code quality, Type safety, Contracts      │
│  └→ Output: PR #6 - "Validation fixes"                   │
│                                                           │
│  Stage 5: Testing                                        │
│  ├→ Agent: Test Generator                                │
│  ├→ Generates: Unit, Integration, UI, E2E tests          │
│  └→ Output: PR #7 - "Test suite"                         │
│                                                           │
│  Stage 6: Visual Diff                                    │
│  ├→ Agent: Visual Diff                                   │
│  ├→ Compares: RN screenshots vs native screenshots       │
│  └→ Reports: Visual regression issues                    │
│                                                           │
│  Stage 7: Documentation                                  │
│  ├→ Agent: Documentation Generator                       │
│  ├→ Creates: Component docs, API docs, Migration notes   │
│  └→ Output: PR #8 - "Documentation"                      │
└──────────────────────────────────────────────────────────┘
        ↓
┌──────────────────────────────────────────────────────────┐
│                  Approval Gates                           │
│                                                           │
│  • Each PR requires manual approval                      │
│  • Stage gates block next stage until approved           │
│  • Can rollback to previous stage if needed              │
│  • Full audit trail in database                          │
└──────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Core Infrastructure
- **n8n**: v1.x - Workflow orchestration engine
- **PostgreSQL**: v14+ - Relational database for state and audit
- **Ollama**: Latest - Local LLM inference server
- **OpenWebUI**: Latest - LLM API gateway

### LLM Models
- **Primary**: `qwen2.5:7b-instruct-q4_K_M` (7B parameters, quantized)
- **Upgrade Option**: `qwen2.5-coder:32b` (32B parameters, better quality)
- **Temperature Range**: 0.1-0.9 (0.2 for analytical, 0.3 for creative)

### Version Control
- **GitHub**: Repository hosting, PR management, GitHub Actions
- **Git**: Version control for generated code and OAM definitions

### Data Layer
- **PostgreSQL Tables**: 15+ tables for state management
- **JSONB Columns**: Flexible schema for shared context
- **Views**: Pre-aggregated metrics and dashboards
- **Indexes**: Optimized for project_id, created_at queries

---

## Intent Routing Architecture

### LLM Classification System

```
┌─────────────────────────────────────────────────────────┐
│           Intent Detection Pipeline                      │
│                                                          │
│  Input:                                                  │
│  ├→ User Message (current)                              │
│  ├→ Conversation History (last 5 messages)              │
│  └→ Session State (if exists)                           │
│                                                          │
│  LLM Analysis:                                          │
│  ├→ Model: qwen2.5:7b-instruct-q4_K_M                   │
│  ├→ Temperature: 0.2 (consistent classification)        │
│  └→ System Prompt: Intent classification instructions   │
│                                                          │
│  Output:                                                 │
│  {                                                       │
│    "intent": "prd_generation" | "e2e_solution" |        │
│               "whitelabel_migration" | "unknown",       │
│    "confidence": 0.0-1.0,                               │
│    "reasoning": "explanation of classification",         │
│    "clarificationNeeded": true/false                    │
│  }                                                       │
│                                                          │
│  Decision Logic:                                         │
│  ├→ if confidence >= 0.7 → Route to workflow            │
│  └→ if confidence < 0.7 → Ask clarifying questions      │
└─────────────────────────────────────────────────────────┘
```

### Routing Table

| Intent | Webhook | Workflow |
|--------|---------|----------|
| `prd_generation` | `/webhook/chat/business-analyst` | Business Analyst → PRD Generator |
| `e2e_solution` | `/webhook/chat/business-analyst` | Business Analyst → PRD Generator → DevOps |
| `whitelabel_migration` | `/webhook/chat/migration-config` | Configuration Assistant → Master Orchestrator |
| `unknown` | N/A | Clarification Response |

---

## Data Flow

### PRD Generation Data Flow

```
1. User Input → Chat Interface
    ↓
2. HTTP POST → Intent Router Webhook
    ↓
3. Session State → PostgreSQL (chat_sessions table)
    ↓
4. Intent Classification → LLM (Ollama)
    ↓
5. Route Decision → Business Analyst Webhook
    ↓
6. Requirements Extraction → PostgreSQL (functional_requirements)
    ↓
7. Project Creation → PostgreSQL (e2e_projects)
    ↓
8. PRD Generator Trigger → HTTP POST
    ↓
9. Shared Context Init → PostgreSQL (shared_context v1)
    ↓
10. For each Expert:
    ├→ Load Context → PostgreSQL
    ├→ LLM Analysis → Ollama
    ├→ Update Context → PostgreSQL (context v++)
    └→ Log Consultation → PostgreSQL (expert_consultations)
    ↓
11. Generate PRD → LLM (Ollama)
    ↓
12. Save PRD → PostgreSQL (prd_documents)
    ↓
13. Generate OAM → LLM (Ollama)
    ↓
14. Save OAM → PostgreSQL (oam_definitions)
    ↓
15. (Optional) Push to GitHub → GitHub API
```

### White-Label Migration Data Flow

```
1. User Input → Chat Interface
    ↓
2. HTTP POST → Intent Router Webhook
    ↓
3. Session State → PostgreSQL (migration_sessions)
    ↓
4. Configuration Complete → Master Orchestrator Webhook
    ↓
5. Migration Record → PostgreSQL (migrations table)
    ↓
6. For each Stage:
    ├→ Agent Execution → HTTP POST to agent webhook
    ├→ Code Generation → LLM (Ollama)
    ├→ GitHub Operations → GitHub API (create PR)
    ├→ Stage Completion → PostgreSQL (approval_gates)
    ├→ Wait for PR Approval → GitHub Webhook
    └→ Next Stage Trigger → Master Orchestrator
    ↓
7. Final Migration Status → PostgreSQL (migrations table)
```

---

## Security Architecture

### Authentication & Authorization
- **Webhook Security**: Token-based authentication (optional)
- **Database Access**: PostgreSQL role-based access control
- **GitHub Integration**: Personal Access Tokens (PATs) securely stored
- **LLM Access**: Local Ollama instance (no external API keys)

### Data Protection
- **SQL Injection Prevention**: Prepared statements, input escaping
- **Secrets Management**: Environment variables, never in code
- **Audit Trail**: All actions logged with timestamps
- **Conversation History**: Stored securely in PostgreSQL

### Network Security
- **Internal Communication**: n8n ↔ PostgreSQL ↔ Ollama (localhost)
- **External Communication**: GitHub API (HTTPS only)
- **Webhook Endpoints**: Configurable authentication

---

## Scalability Considerations

### Vertical Scaling
- **PostgreSQL**: Connection pooling, index optimization
- **Ollama**: GPU acceleration for faster inference
- **n8n**: Execution queue management

### Horizontal Scaling
- **Multiple Ollama Instances**: Load balancing across LLM servers
- **PostgreSQL Read Replicas**: For reporting and analytics
- **n8n Workers**: Distributed execution (enterprise feature)

### Performance Optimization
- **Caching**: LLM response caching for repeated queries
- **Parallel Execution**: Non-dependent experts called simultaneously
- **Database Indexing**: Already optimized for common queries

---

## Observability

### Monitoring Points
1. **Intent Router**: Classification confidence, route distribution
2. **Expert Consultations**: Duration, success rate, failure reasons
3. **Database Performance**: Query times, connection pool usage
4. **LLM Performance**: Token usage, inference time, errors

### Logging
- **n8n Execution Logs**: Real-time workflow execution details
- **PostgreSQL Audit Tables**: expert_consultations, oam_definitions
- **Error Tracking**: Failed executions, validation errors

### Metrics
- **Projects Created**: Count by type (mobile/web/backend)
- **Expert Performance**: Average duration per expert
- **Success Rate**: PRD generation completion rate
- **Migration Success**: PR approval rate, time to completion

---

**Last Updated:** 2025-01-27

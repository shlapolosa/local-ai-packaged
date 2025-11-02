# API Reference

Complete API documentation for all webhook endpoints and data models.

---

## Table of Contents

1. [Intent Router API](#intent-router-api)
2. [PRD Generation APIs](#prd-generation-apis)
3. [White-Label Migration APIs](#white-label-migration-apis)
4. [Common Data Models](#common-data-models)
5. [Error Responses](#error-responses)

---

## Intent Router API

### POST `/webhook/chat/assistant`

**Description:** Main entry point for all user messages. Routes to appropriate workflow based on detected intent.

**Request:**
```json
{
  "message": "I need a PRD for my mobile app",
  "sessionId": "user-session-123",
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ]
}
```

**Response:**
```json
{
  "reply": "I'll help you create a PRD! Let me gather some details...",
  "detectedIntent": "prd_generation",
  "confidence": 0.92,
  "sessionId": "user-session-123",
  "nextWorkflow": "/webhook/chat/business-analyst"
}
```

**Intent Values:**
- `prd_generation` - PRD documentation request
- `e2e_solution` - Full end-to-end solution development
- `whitelabel_migration` - React Native migration
- `unknown` - Unclear intent, needs clarification

**Confidence Threshold:** 0.7 (70%)
- `>= 0.7` → Route to workflow
- `< 0.7` → Ask clarifying questions

---

## PRD Generation APIs

### POST `/webhook/chat/business-analyst`

**Description:** Interactive requirements gathering chat interface.

**Request:**
```json
{
  "message": "Project name is HabitTracker, mobile app for iOS and Android",
  "sessionId": "session-456",
  "state": {
    "step": 1,
    "systemBrief": "Mobile app for tracking daily habits",
    "projectName": null
  }
}
```

**Response:**
```json
{
  "reply": "Great! What are the core features you want to include?",
  "sessionId": "session-456",
  "state": {
    "step": 2,
    "systemBrief": "Mobile app for tracking daily habits",
    "projectName": "HabitTracker",
    "projectType": "mobile",
    "platforms": ["ios", "android"]
  },
  "requirementsComplete": false
}
```

**Session State Fields:**
- `step` (integer): Current step in conversation (0-8)
- `systemBrief` (string): High-level project description
- `projectName` (string): Project name
- `projectType` (string): mobile | web | backend | fullstack | ml | iot
- `platforms` (array): ['ios', 'android', 'web']
- `coreFeatures` (array): List of core features
- `constraints` (array): Business/technical constraints
- `nfrs` (array): Non-functional requirements
- `githubRepo` (string): GitHub repository URL
- `targetBranch` (string): Git branch (default: 'main')
- `requirementsComplete` (boolean): Ready to generate PRD

**When `requirementsComplete: true`:**
- Business Analyst creates project in database
- Automatically triggers PRD Generator Orchestrator
- Returns `project_id` for tracking

---

### POST `/webhook/prd-generator`

**Description:** Orchestrates all expert consultations and PRD generation.

**Request:**
```json
{
  "projectId": "550e8400-e29b-41d4-a716-446655440000",
  "projectName": "HabitTracker",
  "triggeredBy": "business-analyst"
}
```

**Response:**
```json
{
  "success": true,
  "projectId": "550e8400-e29b-41d4-a716-446655440000",
  "projectName": "HabitTracker",
  "prdGenerated": true,
  "oamGenerated": true,
  "status": "completed",
  "expertConsultations": [
    {
      "expert": "compliance_risk_assessor",
      "status": "completed",
      "duration": 45
    },
    {
      "expert": "business_architect",
      "status": "completed",
      "duration": 62
    }
    // ... 7 experts total
  ],
  "outputs": {
    "prdUrl": "https://github.com/myorg/habittracker/blob/main/analysis/prd.md",
    "standardOamUrl": "https://github.com/myorg/habittracker/blob/main/analysis/oam/standard.yaml",
    "platformOamUrl": "https://github.com/myorg/habittracker/blob/main/analysis/oam/platform-specific.yaml"
  }
}
```

**Processing Steps:**
1. Load project and requirements from database
2. Initialize shared context (v1)
3. Query OAM component catalog
4. Call 7 experts sequentially
5. Generate final PRD (markdown)
6. Generate 2 OAM definitions (YAML)
7. (Optional) Push to GitHub
8. Update project status to 'completed'

---

### Expert Consultation APIs

All experts follow the same request/response pattern.

#### POST `/webhook/expert/{expert-name}`

**Expert Names:**
- `/webhook/expert/compliance-risk`
- `/webhook/expert/business-architect`
- `/webhook/expert/experience-designer`
- `/webhook/expert/technology-cto`
- `/webhook/expert/application-architect`
- `/webhook/expert/solution-architect`
- `/webhook/expert/infrastructure-reviewer`

**Request:**
```json
{
  "projectId": "550e8400-e29b-41d4-a716-446655440000",
  "sharedContext": {
    "project_overview": { ... },
    "functional_requirements": [ ... ],
    "non_functional_requirements": [ ... ]
  },
  "contextVersion": 1
}
```

**Response:**
```json
{
  "success": true,
  "expertName": "compliance_risk_assessor",
  "projectId": "550e8400-e29b-41d4-a716-446655440000",
  "updatedContext": {
    "project_overview": { ... },
    "functional_requirements": [ ... ],
    "compliance_requirements": [
      "GDPR compliance for EU users",
      "PCI-DSS for payment processing"
    ],
    "identified_risks": [
      {
        "description": "Data breach risk",
        "severity": "high",
        "mitigation": "Implement end-to-end encryption"
      }
    ]
  },
  "contextVersion": 2,
  "analysis": {
    "regulations": ["GDPR", "PCI-DSS"],
    "threats": [ ... ],
    "controls": [ ... ]
  },
  "recommendations": [
    "Implement OAuth 2.0 authentication",
    "Use AES-256 encryption for data at rest"
  ]
}
```

**Expert-Specific Context Updates:**

| Expert | Adds to Context |
|--------|-----------------|
| Compliance & Risk | `compliance_requirements`, `identified_risks` |
| Business Architect | `business_constraints`, `decision_rationale` |
| Experience Designer | `ux_requirements`, `decision_rationale` |
| Technology CTO | `technology_decisions`, `infrastructure_constraints` |
| Application Architect | `architectural_patterns`, `decision_rationale` |
| Solution Architect | `oam_definitions`, `decision_rationale` |
| Infrastructure Reviewer | `infrastructure_constraints`, `approval_status` |

---

## White-Label Migration APIs

### POST `/webhook/chat/migration-config`

**Description:** Interactive configuration for white-label migration.

**Request:**
```json
{
  "message": "https://github.com/myorg/my-rn-app",
  "sessionId": "migration-789",
  "state": {
    "step": 0,
    "sourceRepo": null
  }
}
```

**Response:**
```json
{
  "reply": "Which platforms do you want to target? (iOS, Android, Web)",
  "sessionId": "migration-789",
  "state": {
    "step": 1,
    "sourceRepo": "https://github.com/myorg/my-rn-app",
    "targetPlatforms": null
  }
}
```

**When Configuration Complete:**
```json
{
  "reply": "Configuration complete! Starting migration...",
  "migrationId": "660e8400-e29b-41d4-a716-446655440001",
  "status": "in_progress",
  "currentStage": "scaffolding"
}
```

---

### POST `/webhook/migration/orchestrator`

**Description:** Master orchestrator for migration workflow.

**Request:**
```json
{
  "migrationId": "660e8400-e29b-41d4-a716-446655440001",
  "sourceRepo": "https://github.com/myorg/my-rn-app",
  "targetPlatforms": ["ios", "android"],
  "config": {
    "monoRepo": true,
    "branchingStrategy": "gitflow",
    "targetRepoName": "my-app-mono-repo"
  }
}
```

**Response:**
```json
{
  "success": true,
  "migrationId": "660e8400-e29b-41d4-a716-446655440001",
  "status": "in_progress",
  "currentStage": "scaffolding",
  "stages": [
    {
      "name": "scaffolding",
      "status": "in_progress",
      "agent": "repo-analyzer"
    },
    {
      "name": "analysis",
      "status": "pending",
      "agent": "contract-generator"
    }
    // ... more stages
  ]
}
```

---

### Agent Webhook APIs

#### POST `/webhook/agent/repo-analyzer`

**Description:** Scaffold mono-repo structure.

**Request:**
```json
{
  "migrationId": "660e8400-e29b-41d4-a716-446655440001",
  "sourceRepo": "https://github.com/myorg/my-rn-app",
  "targetPlatforms": ["ios", "android"]
}
```

**Response:**
```json
{
  "success": true,
  "prNumber": 1,
  "prUrl": "https://github.com/myorg/my-app-mono-repo/pull/1",
  "stage": "scaffolding",
  "nextStage": "analysis"
}
```

---

#### POST `/webhook/agent/contract-generator`

**Description:** Generate platform-agnostic contracts.

**Request:**
```json
{
  "migrationId": "660e8400-e29b-41d4-a716-446655440001",
  "sourceRepo": "https://github.com/myorg/my-rn-app"
}
```

**Response:**
```json
{
  "success": true,
  "contracts": {
    "components": 47,
    "dataModels": 12,
    "apiEndpoints": 8
  },
  "prNumber": 2,
  "prUrl": "https://github.com/myorg/my-app-mono-repo/pull/2",
  "nextStage": "code_generation"
}
```

---

#### POST `/webhook/agent/code-transformer-{platform}`

**Platforms:** `ios`, `android`, `web`

**Request:**
```json
{
  "migrationId": "660e8400-e29b-41d4-a716-446655440001",
  "platform": "ios",
  "contracts": [ ... ]
}
```

**Response:**
```json
{
  "success": true,
  "platform": "ios",
  "filesGenerated": 134,
  "prNumber": 3,
  "prUrl": "https://github.com/myorg/my-app-mono-repo/pull/3",
  "buildStatus": "success"
}
```

---

## Common Data Models

### Project Model

```typescript
interface Project {
  project_id: string;  // UUID
  project_name: string;
  project_type: 'mobile' | 'web' | 'backend' | 'fullstack' | 'ml' | 'iot';
  platforms: string[];  // ['ios', 'android', 'web']
  system_brief: string;
  github_repo_url: string;
  target_branch: string;  // default: 'main'
  status: 'initializing' | 'requirements_gathering' | 'expert_consultation' |
          'prd_generation' | 'oam_generation' | 'completed' | 'failed';
  current_stage: string;
  created_at: string;  // ISO 8601
  updated_at: string;
  completed_at: string | null;
}
```

### Requirement Model

```typescript
interface Requirement {
  requirement_id: string;  // UUID
  project_id: string;  // Foreign key
  requirement_type: 'functional' | 'non_functional' | 'constraint';
  description: string;
  priority: 'high' | 'medium' | 'low';
  source: string;  // 'business_analyst'
  created_at: string;
}
```

### Shared Context Model

```typescript
interface SharedContext {
  context_id: string;  // UUID
  project_id: string;
  version: number;
  context_data: {
    project_overview: {
      name: string;
      brief: string;
      type: string;
      platforms: string[];
    };
    functional_requirements: string[];
    non_functional_requirements: string[];
    constraints: string[];
    compliance_requirements: string[];
    business_constraints: string[];
    ux_requirements: string[];
    technology_decisions: string[];
    architectural_patterns: string[];
    infrastructure_constraints: string[];
    identified_risks: Risk[];
    expert_recommendations: {
      [expertName: string]: string;
    };
    decision_rationale: {
      [decision: string]: string;
    };
    platform_capabilities: {
      available_components: string[];
      foundational: string[];
      compositional: string[];
      infrastructural: string[];
    };
    oam_definitions?: {
      standard: string;  // YAML
      platform_specific: string;  // YAML
    };
  };
  updated_by: string;
  created_at: string;
}
```

### Risk Model

```typescript
interface Risk {
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  mitigation: string;
}
```

### Expert Consultation Model

```typescript
interface ExpertConsultation {
  consultation_id: string;  // UUID
  project_id: string;
  expert_name: 'compliance_risk_assessor' | 'business_architect' |
               'experience_designer' | 'technology_cto' |
               'application_architect' | 'solution_architect' |
               'infrastructure_reviewer' | 'devops_engineer';
  status: 'in_progress' | 'completed' | 'failed';
  input_context_version: number;
  output_context_version: number;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
  error_message: string | null;
  recommendations_summary: string;
}
```

### Migration Model

```typescript
interface Migration {
  migration_id: string;  // UUID
  source_repo_url: string;
  target_repo_url: string;
  target_platforms: string[];
  current_stage: 'scaffolding' | 'analysis' | 'code_generation' |
                 'validation' | 'testing' | 'visual_diff' |
                 'documentation' | 'completed';
  status: 'in_progress' | 'completed' | 'failed';
  config: object;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Project name is required",
    "details": {
      "field": "projectName",
      "value": null
    }
  }
}
```

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Invalid input parameters | 400 |
| `NOT_FOUND` | Resource not found | 404 |
| `DATABASE_ERROR` | Database operation failed | 500 |
| `LLM_ERROR` | LLM inference failed | 500 |
| `TIMEOUT_ERROR` | Operation timed out | 504 |
| `GITHUB_ERROR` | GitHub API operation failed | 500 |
| `INTENT_UNCLEAR` | Cannot determine intent | 400 |
| `CONTEXT_VERSION_MISMATCH` | Shared context version conflict | 409 |

---

## Rate Limiting

**n8n Webhook Endpoints:**
- No built-in rate limiting
- Configure at reverse proxy level if needed

**GitHub API:**
- Authenticated: 5,000 requests/hour
- Unauthenticated: 60 requests/hour

**Ollama LLM:**
- Limited by hardware (GPU/CPU)
- Typically 1-2 concurrent requests for 7B models

---

## Authentication

**Current Implementation:**
- No authentication on webhooks (local development)
- PostgreSQL uses password authentication

**Production Recommendations:**
- Add API key validation to webhooks
- Use JWT tokens for session management
- Implement rate limiting per user
- Enable HTTPS/TLS

---

**Last Updated:** 2025-01-27

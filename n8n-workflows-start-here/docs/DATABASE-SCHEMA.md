# Database Schema Reference

Complete database schema documentation for both PRD Generation and White-Label Migration platforms.

---

## Table of Contents

1. [PRD Generation Schema](#prd-generation-schema)
2. [White-Label Migration Schema](#white-label-migration-schema)
3. [Common Queries](#common-queries)
4. [Views and Aggregations](#views-and-aggregations)
5. [Indexes and Performance](#indexes-and-performance)

---

## PRD Generation Schema

### Core Tables

#### `e2e_projects`
Tracks all PRD generation projects.

```sql
CREATE TABLE e2e_projects (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name VARCHAR(255) NOT NULL,
    project_type VARCHAR(50) CHECK (project_type IN ('mobile', 'web', 'backend', 'fullstack', 'ml', 'iot')),
    platforms TEXT[],  -- ['ios', 'android', 'web']
    system_brief TEXT,
    github_repo_url VARCHAR(500),
    target_branch VARCHAR(100) DEFAULT 'main',
    status VARCHAR(50) DEFAULT 'initializing',
    current_stage VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_e2e_projects_status ON e2e_projects(status);
CREATE INDEX idx_e2e_projects_created_at ON e2e_projects(created_at DESC);
```

**Status Values:**
- `initializing` - Project just created
- `requirements_gathering` - Business Analyst collecting requirements
- `expert_consultation` - Experts being consulted
- `prd_generation` - Final PRD being generated
- `oam_generation` - OAM definitions being created
- `completed` - All stages complete
- `failed` - Error occurred

---

#### `functional_requirements`
Stores requirements extracted by Business Analyst.

```sql
CREATE TABLE functional_requirements (
    requirement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES e2e_projects(project_id) ON DELETE CASCADE,
    requirement_type VARCHAR(50) CHECK (requirement_type IN ('functional', 'non_functional', 'constraint')),
    description TEXT NOT NULL,
    priority VARCHAR(20) CHECK (priority IN ('high', 'medium', 'low')),
    source VARCHAR(100) DEFAULT 'business_analyst',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_functional_requirements_project ON functional_requirements(project_id);
CREATE INDEX idx_functional_requirements_type ON functional_requirements(requirement_type);
```

**Example Data:**
```sql
INSERT INTO functional_requirements (project_id, requirement_type, description, priority)
VALUES ('abc123...', 'functional', 'User authentication with email/password', 'high');
```

---

#### `shared_context`
Cumulative knowledge across expert consultations (JSONB for flexibility).

```sql
CREATE TABLE shared_context (
    context_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES e2e_projects(project_id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    context_data JSONB NOT NULL,
    updated_by VARCHAR(100) NOT NULL,  -- Expert name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, version)
);

CREATE INDEX idx_shared_context_project ON shared_context(project_id);
CREATE INDEX idx_shared_context_version ON shared_context(project_id, version);
CREATE INDEX idx_shared_context_jsonb ON shared_context USING gin(context_data);
```

**Context Data Structure:**
```json
{
  "project_overview": {
    "name": "HabitTracker",
    "brief": "Mobile app for tracking daily habits",
    "type": "mobile",
    "platforms": ["ios", "android"]
  },
  "functional_requirements": ["..."],
  "non_functional_requirements": ["..."],
  "compliance_requirements": ["GDPR compliance", "..."],
  "business_constraints": ["Launch in 3 months", "..."],
  "ux_requirements": ["Mobile-first design", "..."],
  "technology_decisions": ["Use Knative for scaling", "..."],
  "architectural_patterns": ["Event-driven architecture", "..."],
  "infrastructure_constraints": ["Max 10 pods per service", "..."],
  "identified_risks": [
    {
      "description": "API rate limiting",
      "severity": "medium",
      "mitigation": "Implement caching layer"
    }
  ],
  "expert_recommendations": {
    "compliance_risk_assessor": "...",
    "business_architect": "...",
    "experience_designer": "...",
    "technology_cto": "...",
    "application_architect": "...",
    "solution_architect": "...",
    "infrastructure_reviewer": "..."
  },
  "decision_rationale": {
    "database_choice": "PostgreSQL for ACID compliance",
    ...
  },
  "platform_capabilities": {
    "available_components": ["..."],
    "foundational": ["..."],
    "compositional": ["..."],
    "infrastructural": ["..."]
  },
  "oam_definitions": {
    "standard": "# Standard OAM YAML...",
    "platform_specific": "# Platform-specific OAM YAML..."
  }
}
```

**Version Progression:**
- v1: Initial context (project overview, requirements)
- v2: + Compliance & Risk assessment
- v3: + Business Architecture
- v4: + Experience Design
- v5: + Technology Decisions
- v6: + Application Architecture
- v7: + Solution Architecture (OAM)
- v8: + Infrastructure Review
- v9: + DevOps Implementation (optional)

---

#### `expert_consultations`
Audit trail of expert work.

```sql
CREATE TABLE expert_consultations (
    consultation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES e2e_projects(project_id) ON DELETE CASCADE,
    expert_name VARCHAR(100) CHECK (expert_name IN (
        'compliance_risk_assessor',
        'business_architect',
        'experience_designer',
        'technology_cto',
        'application_architect',
        'solution_architect',
        'infrastructure_reviewer',
        'devops_engineer'
    )),
    status VARCHAR(50) DEFAULT 'in_progress',
    input_context_version INTEGER,
    output_context_version INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    error_message TEXT,
    recommendations_summary TEXT
);

CREATE INDEX idx_expert_consultations_project ON expert_consultations(project_id);
CREATE INDEX idx_expert_consultations_expert ON expert_consultations(expert_name);
CREATE INDEX idx_expert_consultations_status ON expert_consultations(status);
```

---

#### `expert_communications`
Bidirectional queries between experts (for parallel consultation).

```sql
CREATE TABLE expert_communications (
    communication_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES e2e_projects(project_id) ON DELETE CASCADE,
    from_expert VARCHAR(100),
    to_expert VARCHAR(100),
    message_type VARCHAR(50) CHECK (message_type IN ('query', 'response', 'notification')),
    message_content JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP
);

CREATE INDEX idx_expert_comms_project ON expert_communications(project_id);
CREATE INDEX idx_expert_comms_to ON expert_communications(to_expert, read_at);
```

---

#### `chat_sessions`
Business Analyst conversation state.

```sql
CREATE TABLE chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES e2e_projects(project_id) ON DELETE SET NULL,
    user_id VARCHAR(255),
    session_state JSONB NOT NULL,
    conversation_history JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_project ON chat_sessions(project_id);
```

**Session State Structure:**
```json
{
  "step": 3,
  "systemBrief": "Mobile app for tracking daily habits",
  "projectName": "HabitTracker",
  "projectType": "mobile",
  "platforms": ["ios", "android"],
  "coreFeatures": [
    "Track daily habits",
    "Reminder notifications",
    "Progress visualization"
  ],
  "constraints": ["Launch in 3 months", "Budget: $50K"],
  "nfrs": ["Support 10K users", "Data encryption"],
  "githubRepo": "https://github.com/myorg/habittracker",
  "targetBranch": "main",
  "requirementsComplete": false
}
```

---

#### `oam_definitions`
Generated OAM YAML files.

```sql
CREATE TABLE oam_definitions (
    definition_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES e2e_projects(project_id) ON DELETE CASCADE,
    definition_type VARCHAR(50) CHECK (definition_type IN ('standard', 'platform_specific')),
    yaml_content TEXT NOT NULL,
    review_status VARCHAR(50) DEFAULT 'pending',
    reviewer_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);

CREATE INDEX idx_oam_definitions_project ON oam_definitions(project_id);
CREATE INDEX idx_oam_definitions_type ON oam_definitions(definition_type);
```

---

#### `prd_documents`
Generated PRD markdown files.

```sql
CREATE TABLE prd_documents (
    prd_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES e2e_projects(project_id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    markdown_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'prd_generator'
);

CREATE INDEX idx_prd_documents_project ON prd_documents(project_id);
CREATE INDEX idx_prd_documents_version ON prd_documents(project_id, version DESC);
```

---

#### `oam_component_catalog`
Available platform components (from ComponentDefinitions).

```sql
CREATE TABLE oam_component_catalog (
    component_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_name VARCHAR(255) NOT NULL UNIQUE,
    component_type VARCHAR(50) CHECK (component_type IN ('foundational', 'compositional', 'infrastructural')),
    description TEXT,
    capabilities JSONB,
    parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_oam_component_catalog_type ON oam_component_catalog(component_type);
```

**Example Components:**
```sql
INSERT INTO oam_component_catalog (component_name, component_type, description, capabilities)
VALUES
  ('webservice', 'foundational', 'Knative Service workload', '["http", "scaling"]'),
  ('neon-postgres', 'foundational', 'Serverless PostgreSQL database', '["database", "postgresql"]'),
  ('kafka-topic', 'compositional', 'Kafka topic for event streaming', '["messaging", "kafka"]');
```

---

### Views

#### `v_project_dashboard`
Real-time project status overview.

```sql
CREATE OR REPLACE VIEW v_project_dashboard AS
SELECT
    p.project_id,
    p.project_name,
    p.project_type,
    p.platforms,
    p.status,
    p.current_stage,
    p.created_at,
    COUNT(DISTINCT fr.requirement_id) as total_requirements,
    COUNT(DISTINCT ec.consultation_id) as total_consultations,
    COUNT(DISTINCT ec.consultation_id) FILTER (WHERE ec.status = 'completed') as completed_consultations,
    MAX(sc.version) as latest_context_version,
    p.updated_at
FROM e2e_projects p
LEFT JOIN functional_requirements fr ON p.project_id = fr.project_id
LEFT JOIN expert_consultations ec ON p.project_id = ec.project_id
LEFT JOIN shared_context sc ON p.project_id = sc.project_id
GROUP BY p.project_id;
```

**Usage:**
```sql
SELECT * FROM v_project_dashboard ORDER BY created_at DESC;
```

---

#### `v_expert_performance`
Expert metrics and SLAs.

```sql
CREATE OR REPLACE VIEW v_expert_performance AS
SELECT
    expert_name,
    COUNT(*) as total_consultations,
    COUNT(*) FILTER (WHERE status = 'completed') as successful,
    COUNT(*) FILTER (WHERE status = 'failed') as failed,
    AVG(duration_seconds) as avg_duration_seconds,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_seconds) as median_duration_seconds,
    MAX(duration_seconds) as max_duration_seconds
FROM expert_consultations
GROUP BY expert_name;
```

---

#### `v_requirements_coverage`
Requirement traceability.

```sql
CREATE OR REPLACE VIEW v_requirements_coverage AS
SELECT
    p.project_id,
    p.project_name,
    fr.requirement_type,
    COUNT(*) as requirement_count,
    ARRAY_AGG(fr.description ORDER BY fr.priority DESC) as requirements_list
FROM e2e_projects p
JOIN functional_requirements fr ON p.project_id = fr.project_id
GROUP BY p.project_id, p.project_name, fr.requirement_type;
```

---

## White-Label Migration Schema

### Core Tables

#### `migrations`
Tracks white-label migration projects.

```sql
CREATE TABLE migrations (
    migration_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_repo_url VARCHAR(500) NOT NULL,
    target_repo_url VARCHAR(500),
    target_platforms TEXT[],  -- ['ios', 'android', 'web']
    current_stage VARCHAR(100) DEFAULT 'scaffolding',
    status VARCHAR(50) DEFAULT 'in_progress',
    config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_migrations_status ON migrations(status);
CREATE INDEX idx_migrations_stage ON migrations(current_stage);
```

**Stages:**
- `scaffolding` - Creating mono-repo structure
- `analysis` - Analyzing React Native code
- `code_generation` - Generating platform code
- `validation` - Validating generated code
- `testing` - Running tests
- `visual_diff` - Comparing visuals
- `documentation` - Generating docs
- `completed` - Migration complete

---

#### `approval_gates`
PR approval tracking for stage gates.

```sql
CREATE TABLE approval_gates (
    gate_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    migration_id UUID REFERENCES migrations(migration_id) ON DELETE CASCADE,
    stage_name VARCHAR(100) NOT NULL,
    pr_number INTEGER,
    pr_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending',
    approved_by VARCHAR(255),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_approval_gates_migration ON approval_gates(migration_id);
CREATE INDEX idx_approval_gates_status ON approval_gates(status);
```

---

## Common Queries

### PRD Generation Queries

#### View Active Projects
```sql
SELECT
    project_name,
    project_type,
    status,
    current_stage,
    created_at
FROM v_project_dashboard
WHERE status != 'completed'
ORDER BY created_at DESC;
```

#### Check Expert Progress for a Project
```sql
SELECT
    expert_name,
    status,
    ROUND(EXTRACT(EPOCH FROM (completed_at - started_at))) as duration_seconds,
    recommendations_summary
FROM expert_consultations
WHERE project_id = 'YOUR_PROJECT_ID'
ORDER BY started_at;
```

#### View Context Evolution
```sql
SELECT
    version,
    updated_by,
    created_at,
    context_data->'expert_recommendations' as recommendations
FROM shared_context
WHERE project_id = 'YOUR_PROJECT_ID'
ORDER BY version;
```

#### Get Latest PRD
```sql
SELECT
    markdown_content
FROM prd_documents
WHERE project_id = 'YOUR_PROJECT_ID'
ORDER BY version DESC
LIMIT 1;
```

#### View OAM Definitions
```sql
SELECT
    definition_type,
    yaml_content,
    review_status
FROM oam_definitions
WHERE project_id = 'YOUR_PROJECT_ID';
```

---

### White-Label Migration Queries

#### View Migration Status
```sql
SELECT
    source_repo_url,
    current_stage,
    status,
    target_platforms,
    created_at
FROM migrations
WHERE status = 'in_progress'
ORDER BY created_at DESC;
```

#### Check Approval Gates
```sql
SELECT
    stage_name,
    pr_number,
    pr_url,
    status,
    approved_by,
    approved_at
FROM approval_gates
WHERE migration_id = 'YOUR_MIGRATION_ID'
ORDER BY created_at;
```

---

## Indexes and Performance

### Existing Indexes
- All `project_id` foreign keys indexed
- Status and timestamp columns indexed
- JSONB columns use GIN indexes for fast queries

### Query Optimization Tips

1. **Use Views**: Pre-aggregated views for dashboards
2. **JSONB Queries**: Use `->` and `->>` operators efficiently
3. **Pagination**: Always use `LIMIT` and `OFFSET` for large result sets
4. **Connection Pooling**: Configure PostgreSQL connection pooling in n8n

---

**Last Updated:** 2025-01-27

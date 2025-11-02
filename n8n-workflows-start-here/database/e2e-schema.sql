-- End-to-End Agent Pipeline Database Schema
-- Compatible with existing migration platform schema

-- Projects: Track each end-to-end solution development
CREATE TABLE IF NOT EXISTS e2e_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name TEXT NOT NULL,
    system_brief TEXT NOT NULL, -- Raw user input
    status TEXT NOT NULL CHECK (status IN ('requirements_gathering', 'prd_generation', 'oam_design', 'infrastructure_review', 'completed', 'failed')),
    current_stage TEXT, -- Current expert being consulted
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,

    -- GitHub integration
    github_repo_url TEXT, -- Target repository for OAM definitions
    target_branch TEXT DEFAULT 'main',

    -- Configuration
    platforms TEXT[], -- ['ios', 'android', 'web'] or null for backend-only
    project_type TEXT CHECK (project_type IN ('mobile', 'web', 'backend', 'fullstack', 'ml', 'iot')),

    -- Outputs
    prd_url TEXT, -- GitHub URL to PRD
    oam_standard_url TEXT, -- GitHub URL to standard OAM
    oam_platform_url TEXT, -- GitHub URL to platform-specific OAM

    UNIQUE(project_name)
);

-- Functional Requirements: Output from Business Analyst
CREATE TABLE IF NOT EXISTS functional_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES e2e_projects(id) ON DELETE CASCADE,
    requirement_type TEXT NOT NULL CHECK (requirement_type IN ('functional', 'non_functional', 'constraint', 'assumption', 'risk')),
    category TEXT, -- e.g., 'authentication', 'data_processing', 'ui', 'integration'
    priority TEXT CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    description TEXT NOT NULL,
    acceptance_criteria TEXT[],
    source TEXT, -- Traceability to system brief section
    created_at TIMESTAMP DEFAULT NOW(),
    created_by TEXT DEFAULT 'business-analyst'
);

-- Shared Context: Cumulative knowledge shared across all agents
CREATE TABLE IF NOT EXISTS shared_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES e2e_projects(id) ON DELETE CASCADE,
    context_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_by TEXT NOT NULL, -- Which agent updated this

    -- Context structure (stored in context_data JSONB):
    -- {
    --   "project_overview": "...",
    --   "compliance_requirements": [],
    --   "business_constraints": [],
    --   "ux_requirements": [],
    --   "technology_decisions": [],
    --   "architectural_patterns": [],
    --   "infrastructure_constraints": [],
    --   "identified_risks": [],
    --   "key_assumptions": [],
    --   "expert_recommendations": {},
    --   "decision_rationale": {}
    -- }

    UNIQUE(project_id, version)
);

-- Create index on project_id and version for fast lookups
CREATE INDEX IF NOT EXISTS idx_shared_context_project_version ON shared_context(project_id, version DESC);

-- Expert Consultations: Audit trail of each agent's work
CREATE TABLE IF NOT EXISTS expert_consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES e2e_projects(id) ON DELETE CASCADE,
    expert_name TEXT NOT NULL CHECK (expert_name IN (
        'business-analyst',
        'compliance-risk-assessor',
        'business-architect',
        'experience-designer',
        'technology-cto',
        'application-architect',
        'solution-architect',
        'infrastructure-reviewer'
    )),
    status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_seconds INTEGER,

    -- Inputs and Outputs
    input_context JSONB, -- Snapshot of context when started
    output_analysis TEXT, -- Markdown analysis document
    output_artifacts JSONB, -- Generated files/diagrams

    -- Metadata
    iteration_number INTEGER DEFAULT 1, -- For iterative reviews
    model_used TEXT DEFAULT 'qwen2.5:7b-instruct-q4_K_M',
    temperature FLOAT DEFAULT 0.3,

    -- Traceability
    source_requirements TEXT[], -- Links to functional_requirements.id
    shared_context_version INTEGER, -- Version of context used

    UNIQUE(project_id, expert_name, iteration_number)
);

CREATE INDEX IF NOT EXISTS idx_expert_consultations_project ON expert_consultations(project_id, started_at DESC);

-- Expert Communications: Bidirectional queries between agents
CREATE TABLE IF NOT EXISTS expert_communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES e2e_projects(id) ON DELETE CASCADE,
    from_expert TEXT NOT NULL,
    to_expert TEXT NOT NULL,
    communication_type TEXT NOT NULL CHECK (communication_type IN ('query', 'response', 'clarification', 'feedback')),
    message TEXT NOT NULL,
    context_reference JSONB, -- Reference to specific context elements
    created_at TIMESTAMP DEFAULT NOW(),
    parent_id UUID REFERENCES expert_communications(id) -- For threading conversations
);

CREATE INDEX IF NOT EXISTS idx_expert_comms_project ON expert_communications(project_id, created_at DESC);

-- Chat Sessions: Track Business Analyst conversations
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES e2e_projects(id) ON DELETE CASCADE,
    session_state JSONB DEFAULT '{}'::jsonb,
    conversation_history JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed BOOLEAN DEFAULT FALSE
);

-- Session state structure:
-- {
--   "step": 0,
--   "systemBrief": null,
--   "projectName": null,
--   "projectType": null,
--   "platforms": [],
--   "githubRepo": null,
--   "targetBranch": "main",
--   "coreFeatures": [],
--   "constraints": [],
--   "requirementsComplete": false
-- }

CREATE INDEX IF NOT EXISTS idx_chat_sessions_project ON chat_sessions(project_id);

-- OAM Definitions: Track generated OAM files
CREATE TABLE IF NOT EXISTS oam_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES e2e_projects(id) ON DELETE CASCADE,
    definition_type TEXT NOT NULL CHECK (definition_type IN ('standard', 'platform-specific')),
    yaml_content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by TEXT DEFAULT 'solution-architect',

    -- Review status
    review_status TEXT CHECK (review_status IN ('pending', 'approved', 'needs_changes')),
    review_iteration INTEGER DEFAULT 1,
    reviewer_feedback TEXT,

    -- GitHub integration
    pr_number INTEGER,
    pr_url TEXT,
    merged BOOLEAN DEFAULT FALSE,

    UNIQUE(project_id, definition_type, version)
);

CREATE INDEX IF NOT EXISTS idx_oam_definitions_project ON oam_definitions(project_id, created_at DESC);

-- PRD Documents: Track generated PRDs
CREATE TABLE IF NOT EXISTS prd_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES e2e_projects(id) ON DELETE CASCADE,
    markdown_content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),

    -- Sections populated
    sections_complete JSONB DEFAULT '{}'::jsonb,
    -- {
    --   "overview": true,
    --   "core_features": true,
    --   "technical_architecture": true,
    --   "user_experience": true,
    --   "development_roadmap": true,
    --   "risks_and_mitigations": true,
    --   "logical_dependency_chain": true
    -- }

    -- GitHub integration
    pr_number INTEGER,
    pr_url TEXT,
    merged BOOLEAN DEFAULT FALSE,

    UNIQUE(project_id, version)
);

CREATE INDEX IF NOT EXISTS idx_prd_documents_project ON prd_documents(project_id, created_at DESC);

-- Component Catalog Cache: Available OAM components (refreshed periodically)
CREATE TABLE IF NOT EXISTS oam_component_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_name TEXT NOT NULL UNIQUE,
    component_type TEXT NOT NULL CHECK (component_type IN ('foundational', 'compositional', 'infrastructural')),
    description TEXT,
    capabilities JSONB,
    constraints JSONB,
    example_usage TEXT,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Seed initial component catalog (will be updated by discovery workflow)
INSERT INTO oam_component_catalog (component_name, component_type, description, capabilities) VALUES
('webservice', 'foundational', 'Knative-based web service', '{"autoscaling": true, "http": true}'),
('webservice-k8s', 'foundational', 'Kubernetes Deployment-based service', '{"persistent": true, "stateful": true}'),
('rasa-chatbot', 'compositional', 'Rasa-based conversational AI', '{"nlu": true, "dialogue": true}'),
('identity-service', 'compositional', 'Authentication and authorization', '{"oauth2": true, "jwt": true}'),
('graphql-gateway', 'compositional', 'GraphQL API gateway', '{"federation": true, "caching": true}'),
('realtime-platform', 'compositional', 'Real-time data processing', '{"streaming": true, "websockets": true}'),
('postgresql', 'infrastructural', 'PostgreSQL database', '{"relational": true, "acid": true}'),
('mongodb', 'infrastructural', 'MongoDB NoSQL database', '{"document": true, "scalable": true}'),
('redis', 'infrastructural', 'Redis cache', '{"cache": true, "pubsub": true}'),
('kafka', 'infrastructural', 'Apache Kafka event streaming', '{"streaming": true, "distributed": true}'),
('neon-postgres', 'infrastructural', 'Neon serverless PostgreSQL', '{"serverless": true, "branching": true}')
ON CONFLICT (component_name) DO NOTHING;

-- Intent Detection Logs: Track intent routing (extends existing intent_logs if present)
CREATE TABLE IF NOT EXISTS e2e_intent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT,
    detected_intent TEXT CHECK (detected_intent IN ('whitelabel_migration', 'e2e_solution', 'help', 'unknown')),
    confidence FLOAT,
    user_message TEXT,
    routed_to_workflow TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_intent_logs_session ON e2e_intent_logs(session_id);

-- Views for monitoring and reporting

-- Project Dashboard: Current status of all projects
CREATE OR REPLACE VIEW v_project_dashboard AS
SELECT
    p.id,
    p.project_name,
    p.status,
    p.current_stage,
    p.project_type,
    p.created_at,
    p.updated_at,
    COUNT(DISTINCT ec.id) as total_consultations,
    COUNT(DISTINCT CASE WHEN ec.status = 'completed' THEN ec.id END) as completed_consultations,
    COUNT(DISTINCT fr.id) as total_requirements,
    MAX(sc.version) as context_version,
    p.prd_url,
    p.oam_standard_url,
    p.oam_platform_url
FROM e2e_projects p
LEFT JOIN expert_consultations ec ON p.id = ec.project_id
LEFT JOIN functional_requirements fr ON p.id = fr.project_id
LEFT JOIN shared_context sc ON p.id = sc.project_id
GROUP BY p.id
ORDER BY p.created_at DESC;

-- Expert Performance: Track consultation metrics
CREATE OR REPLACE VIEW v_expert_performance AS
SELECT
    expert_name,
    COUNT(*) as total_consultations,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
    AVG(duration_seconds) as avg_duration_seconds,
    MAX(iteration_number) as max_iterations
FROM expert_consultations
GROUP BY expert_name
ORDER BY expert_name;

-- Requirements Coverage: Track requirement traceability
CREATE OR REPLACE VIEW v_requirements_coverage AS
SELECT
    p.project_name,
    fr.requirement_type,
    fr.priority,
    COUNT(DISTINCT fr.id) as requirement_count,
    COUNT(DISTINCT ec.id) as consultations_referencing
FROM functional_requirements fr
JOIN e2e_projects p ON fr.project_id = p.id
LEFT JOIN expert_consultations ec ON p.id = ec.project_id
    AND fr.id::text = ANY(ec.source_requirements)
GROUP BY p.project_name, fr.requirement_type, fr.priority
ORDER BY p.project_name, fr.priority;

-- Grant permissions (adjust as needed for your PostgreSQL setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO n8n_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO n8n_user;

-- Comments for documentation
COMMENT ON TABLE e2e_projects IS 'Tracks each end-to-end solution development project';
COMMENT ON TABLE functional_requirements IS 'Requirements extracted by Business Analyst from system brief';
COMMENT ON TABLE shared_context IS 'Cumulative knowledge shared across all expert agents';
COMMENT ON TABLE expert_consultations IS 'Audit trail of expert agent consultations';
COMMENT ON TABLE expert_communications IS 'Bidirectional communication between experts';
COMMENT ON TABLE chat_sessions IS 'Business Analyst chat conversations';
COMMENT ON TABLE oam_definitions IS 'Generated OAM definition files';
COMMENT ON TABLE prd_documents IS 'Generated Product Requirements Documents';
COMMENT ON TABLE oam_component_catalog IS 'Available OAM components on the platform';

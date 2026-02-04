-- Architecture Pipeline Database Schema
-- Required by: Architecture Pipeline (R4SsOqGqQIkRwUPT)
-- Run this against your PostgreSQL database after fresh install

-- Create the architecture schema
CREATE SCHEMA IF NOT EXISTS architecture;

-- ============================================
-- TABLES
-- ============================================

-- Projects table: Tracks architecture projects
CREATE TABLE IF NOT EXISTS architecture.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Jobs table: Tracks pipeline execution jobs
CREATE TABLE IF NOT EXISTS architecture.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES architecture.projects(id) ON DELETE CASCADE,
    stage TEXT NOT NULL,  -- 'business-analysis', 'architecture', 'solution-architecture', etc.
    input_job_id UUID REFERENCES architecture.jobs(id),
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed'
    meta JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Artifacts table: Stores generated architecture artifacts
CREATE TABLE IF NOT EXISTS architecture.artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES architecture.projects(id) ON DELETE CASCADE,
    type TEXT NOT NULL,  -- 'brd', 'business_arch', 'application_arch', 'data_arch',
                         -- 'infrastructure_arch', 'sequence_diagrams', 'archimate_xml_full',
                         -- 'motivation_layer', 'strategy_layer', 'business_layer', 'application_layer'
    version INTEGER NOT NULL DEFAULT 1,
    content JSONB NOT NULL,
    content_hash TEXT,
    meta JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_arch_projects_slug ON architecture.projects(slug);
CREATE INDEX IF NOT EXISTS idx_arch_projects_updated ON architecture.projects(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_arch_jobs_project ON architecture.jobs(project_id);
CREATE INDEX IF NOT EXISTS idx_arch_jobs_stage ON architecture.jobs(stage);
CREATE INDEX IF NOT EXISTS idx_arch_jobs_status ON architecture.jobs(status);
CREATE INDEX IF NOT EXISTS idx_arch_jobs_stage_status ON architecture.jobs(project_id, stage, status);
CREATE INDEX IF NOT EXISTS idx_arch_jobs_created ON architecture.jobs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_arch_artifacts_project ON architecture.artifacts(project_id);
CREATE INDEX IF NOT EXISTS idx_arch_artifacts_type ON architecture.artifacts(type);
CREATE INDEX IF NOT EXISTS idx_arch_artifacts_project_type ON architecture.artifacts(project_id, type);
CREATE INDEX IF NOT EXISTS idx_arch_artifacts_created ON architecture.artifacts(created_at DESC);

-- Unique constraint for artifact versioning (one version per project+type combo)
CREATE UNIQUE INDEX IF NOT EXISTS idx_arch_artifacts_unique_version
ON architecture.artifacts(project_id, type, version);

-- ============================================
-- TRIGGERS
-- ============================================

-- Update trigger for projects table
CREATE OR REPLACE FUNCTION architecture.update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_projects_modtime ON architecture.projects;
CREATE TRIGGER update_projects_modtime
    BEFORE UPDATE ON architecture.projects
    FOR EACH ROW
    EXECUTE FUNCTION architecture.update_modified_column();

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON SCHEMA architecture IS 'Architecture Pipeline schema for TOGAF/ArchiMate artifacts';
COMMENT ON TABLE architecture.projects IS 'Architecture projects tracked by the pipeline';
COMMENT ON TABLE architecture.jobs IS 'Pipeline execution jobs (business-analysis, architecture, solution-architecture stages)';
COMMENT ON TABLE architecture.artifacts IS 'Generated architecture artifacts (BRD, layers, diagrams, ArchiMate XML)';

COMMENT ON COLUMN architecture.artifacts.type IS 'Artifact type: brd, business_arch, application_arch, data_arch, infrastructure_arch, sequence_diagrams, archimate_xml_full, motivation_layer, strategy_layer, business_layer, application_layer';
COMMENT ON COLUMN architecture.jobs.stage IS 'Pipeline stage: business-analysis, architecture, solution-architecture';
COMMENT ON COLUMN architecture.jobs.status IS 'Job status: pending, running, completed, failed';

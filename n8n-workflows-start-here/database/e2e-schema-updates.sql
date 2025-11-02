-- Updates to E2E Schema for DevOps Engineer and GitHub Integration

-- Add devops-engineer to expert_name constraint
ALTER TABLE expert_consultations DROP CONSTRAINT IF EXISTS expert_consultations_expert_name_check;
ALTER TABLE expert_consultations ADD CONSTRAINT expert_consultations_expert_name_check
CHECK (expert_name IN (
    'business-analyst',
    'devops-engineer',
    'compliance-risk-assessor',
    'business-architect',
    'experience-designer',
    'technology-cto',
    'application-architect',
    'solution-architect',
    'infrastructure-reviewer'
));

-- Add GitHub docs URL to projects table
ALTER TABLE e2e_projects ADD COLUMN IF NOT EXISTS github_docs_url TEXT;

-- Add infrastructure_ready flag
ALTER TABLE e2e_projects ADD COLUMN IF NOT EXISTS infrastructure_ready BOOLEAN DEFAULT FALSE;

-- Create table for tracking GitHub docs writes
CREATE TABLE IF NOT EXISTS github_docs_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES e2e_projects(id) ON DELETE CASCADE,
    expert_name TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(project_id, file_path)
);

CREATE INDEX IF NOT EXISTS idx_github_docs_project ON github_docs_files(project_id, created_at DESC);

-- Update v_project_dashboard view to include infrastructure status
DROP VIEW IF EXISTS v_project_dashboard;
CREATE VIEW v_project_dashboard AS
SELECT
    p.id,
    p.project_name,
    p.status,
    p.current_stage,
    p.project_type,
    p.infrastructure_ready,
    p.github_docs_url,
    p.created_at,
    p.updated_at,
    COUNT(DISTINCT ec.id) as total_consultations,
    COUNT(DISTINCT CASE WHEN ec.status = 'completed' THEN ec.id END) as completed_consultations,
    COUNT(DISTINCT fr.id) as total_requirements,
    MAX(sc.version) as context_version,
    COUNT(DISTINCT gdf.id) as docs_files_written,
    p.prd_url,
    p.oam_standard_url,
    p.oam_platform_url
FROM e2e_projects p
LEFT JOIN expert_consultations ec ON p.id = ec.project_id
LEFT JOIN functional_requirements fr ON p.id = fr.project_id
LEFT JOIN shared_context sc ON p.id = sc.project_id
LEFT JOIN github_docs_files gdf ON p.id = gdf.project_id
GROUP BY p.id
ORDER BY p.created_at DESC;

-- Add comment
COMMENT ON TABLE github_docs_files IS 'Tracks expert analysis documents written to GitHub docs folder';
COMMENT ON COLUMN e2e_projects.infrastructure_ready IS 'Flag indicating DevOps has created application container';
COMMENT ON COLUMN e2e_projects.github_docs_url IS 'URL to GitHub docs/analysis folder';

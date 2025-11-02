-- Migration Platform Database Schema
-- Run this against your PostgreSQL database

-- Create migrations table
CREATE TABLE IF NOT EXISTS migrations (
  id UUID PRIMARY KEY,
  user_id TEXT,
  repo_rn TEXT NOT NULL,
  repo_native TEXT,
  monorepo_url TEXT NOT NULL,
  strategy JSONB,
  platforms JSONB,
  status TEXT NOT NULL DEFAULT 'pending', -- pending, running, waiting_approval, completed, failed
  n8n_execution_id TEXT,
  current_stage INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

-- Create approval_gates table (tracks PRs)
CREATE TABLE IF NOT EXISTS approval_gates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  migration_id UUID NOT NULL REFERENCES migrations(id) ON DELETE CASCADE,
  gate_name TEXT NOT NULL, -- stage_1_analysis, stage_2_contracts, etc.
  pr_number INTEGER,
  pr_url TEXT,
  status TEXT NOT NULL DEFAULT 'pending', -- pending, approved, merged, closed
  webhook_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  approved_at TIMESTAMP,
  approver TEXT
);

-- Create artifacts table (stores generated code, analysis, etc.)
CREATE TABLE IF NOT EXISTS artifacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  migration_id UUID NOT NULL REFERENCES migrations(id) ON DELETE CASCADE,
  artifact_type TEXT NOT NULL, -- component_analysis, contract, generated_code, visual_diff, test, documentation
  artifact_name TEXT,
  artifact_data JSONB NOT NULL,
  file_path TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create execution_logs table (optional, for debugging)
CREATE TABLE IF NOT EXISTS execution_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  migration_id UUID REFERENCES migrations(id) ON DELETE CASCADE,
  workflow_name TEXT,
  status TEXT, -- started, completed, failed
  input_data JSONB,
  output_data JSONB,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_migrations_status ON migrations(status);
CREATE INDEX IF NOT EXISTS idx_migrations_created ON migrations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_approval_gates_migration ON approval_gates(migration_id);
CREATE INDEX IF NOT EXISTS idx_approval_gates_status ON approval_gates(status);
CREATE INDEX IF NOT EXISTS idx_approval_gates_pr ON approval_gates(pr_number);
CREATE INDEX IF NOT EXISTS idx_artifacts_migration ON artifacts(migration_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(artifact_type);
CREATE INDEX IF NOT EXISTS idx_execution_logs_migration ON execution_logs(migration_id);

-- Update trigger for migrations table
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_migrations_modtime
    BEFORE UPDATE ON migrations
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Sample query to check migration status
-- SELECT m.id, m.status, m.current_stage,
--        COUNT(ag.id) as total_gates,
--        COUNT(CASE WHEN ag.status = 'merged' THEN 1 END) as merged_gates
-- FROM migrations m
-- LEFT JOIN approval_gates ag ON m.id = ag.migration_id
-- GROUP BY m.id;

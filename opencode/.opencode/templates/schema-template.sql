-- Database Schema Template
-- Generated from architecture artifacts

-- ============================================
-- TABLES
-- ============================================

CREATE TABLE {table_name} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    {field1} VARCHAR(255) NOT NULL,
    {field2} TEXT,
    {field3} VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Foreign key example
CREATE TABLE {child_table} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    {parent_table}_id UUID NOT NULL REFERENCES {parent_table}(id) ON DELETE CASCADE,
    {field1} VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_{table}_status ON {table_name}(status);
CREATE INDEX idx_{table}_created ON {table_name}(created_at);
CREATE INDEX idx_{child}_parent ON {child_table}({parent_table}_id);

-- ============================================
-- TRIGGERS (for updated_at)
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_{table}_updated
    BEFORE UPDATE ON {table_name}
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

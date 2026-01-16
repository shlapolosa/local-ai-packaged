---
name: sql-schema
description: Generate SQL DDL schema from data architecture and requirements
license: MIT
---

# SQL Schema Design Skill

## CRITICAL INSTRUCTIONS
1. **DO NOT** ask the user any questions
2. **DO NOT** request additional information
3. **DO NOT** add preamble text like "Here is the schema..." or "To address this request..."
4. **DO NOT** wrap output in code blocks (no ```) - output raw SQL directly
5. **DO NOT** generate Python/JavaScript code to output the SQL
6. **USE THE USER'S INPUT** - extract tables, columns from THEIR message
7. **STAY ON TOPIC** - the schema must be about the user's project (healthcare, appointments, providers, etc)
8. **IMMEDIATELY** output the SQL DDL (not code or explanation)
9. Your **FIRST CHARACTERS** must be `-- Schema:` - start the SQL directly

**IMPORTANT**: Output ONLY raw PostgreSQL DDL. No preamble. No code blocks. First line is `-- Schema:`.

## Output Format
Output MUST be valid PostgreSQL DDL starting with `-- Schema:`.

## Example Output

```sql
-- Schema: patient_portal
-- Generated from solution architecture
-- Version: 1.0.0

-- =============================================================================
-- EXTENSIONS
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- ENUMS
-- =============================================================================
CREATE TYPE appointment_status AS ENUM (
    'pending',      -- Awaiting confirmation
    'confirmed',    -- Patient confirmed
    'cancelled',    -- Cancelled by patient or provider
    'completed',    -- Visit completed
    'no_show'       -- Patient did not attend
);

CREATE TYPE visit_type AS ENUM (
    'routine',      -- Regular checkup
    'follow_up',    -- Follow-up visit
    'urgent',       -- Same-day urgent
    'telehealth'    -- Virtual visit
);

CREATE TYPE contact_preference AS ENUM ('email', 'sms', 'both', 'none');

-- =============================================================================
-- TABLES
-- =============================================================================

-- Providers (physicians, nurses, etc.)
CREATE TABLE providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(50) UNIQUE,          -- EHR system ID
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    specialty VARCHAR(100),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT true,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT providers_name_not_empty
        CHECK (LENGTH(TRIM(first_name)) > 0 AND LENGTH(TRIM(last_name)) > 0)
);

-- Provider availability (recurring weekly schedule)
CREATE TABLE provider_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    day_of_week SMALLINT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),  -- 0=Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_duration_minutes SMALLINT DEFAULT 30,
    visit_types visit_type[] DEFAULT ARRAY['routine'::visit_type],
    location VARCHAR(200),
    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_time_range CHECK (start_time < end_time),
    CONSTRAINT valid_duration CHECK (slot_duration_minutes BETWEEN 10 AND 120)
);

-- Blocked times (exceptions to availability)
CREATE TABLE blocked_times (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    start_datetime TIMESTAMPTZ NOT NULL,
    end_datetime TIMESTAMPTZ NOT NULL,
    reason VARCHAR(500),
    is_recurring BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_blocked_range CHECK (start_datetime < end_datetime)
);

-- Appointments
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    confirmation_number VARCHAR(20) UNIQUE NOT NULL,

    -- Relationships
    provider_id UUID NOT NULL REFERENCES providers(id),
    patient_id VARCHAR(100) NOT NULL,        -- External patient ID

    -- Scheduling
    scheduled_start TIMESTAMPTZ NOT NULL,
    scheduled_end TIMESTAMPTZ NOT NULL,
    visit_type visit_type NOT NULL DEFAULT 'routine',
    location VARCHAR(200),

    -- Status
    status appointment_status NOT NULL DEFAULT 'pending',
    reason_for_visit TEXT,
    cancellation_reason TEXT,
    cancelled_at TIMESTAMPTZ,
    cancelled_by VARCHAR(100),

    -- Communication
    contact_preference contact_preference DEFAULT 'email',
    reminder_sent_at TIMESTAMPTZ,
    confirmation_sent_at TIMESTAMPTZ,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),

    CONSTRAINT valid_appointment_range CHECK (scheduled_start < scheduled_end)
);

-- Appointment history (audit trail)
CREATE TABLE appointment_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_id UUID NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
    previous_status appointment_status,
    new_status appointment_status NOT NULL,
    changed_by VARCHAR(100),
    change_reason TEXT,
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Provider lookups
CREATE INDEX idx_providers_external_id ON providers(external_id) WHERE external_id IS NOT NULL;
CREATE INDEX idx_providers_active ON providers(is_active) WHERE is_active = true;

-- Availability queries
CREATE INDEX idx_availability_provider_day ON provider_availability(provider_id, day_of_week);
CREATE INDEX idx_availability_active ON provider_availability(is_active) WHERE is_active = true;

-- Blocked time queries
CREATE INDEX idx_blocked_provider_range ON blocked_times(provider_id, start_datetime, end_datetime);

-- Appointment queries (most common)
CREATE INDEX idx_appointments_provider_date ON appointments(provider_id, scheduled_start);
CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_status ON appointments(status) WHERE status IN ('pending', 'confirmed');
CREATE INDEX idx_appointments_confirmation ON appointments(confirmation_number);

-- Audit trail
CREATE INDEX idx_history_appointment ON appointment_history(appointment_id, changed_at DESC);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER providers_updated_at
    BEFORE UPDATE ON providers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER availability_updated_at
    BEFORE UPDATE ON provider_availability
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER appointments_updated_at
    BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Generate confirmation number
CREATE OR REPLACE FUNCTION generate_confirmation_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.confirmation_number IS NULL THEN
        NEW.confirmation_number = 'APT-' || UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 8));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER appointments_confirmation_number
    BEFORE INSERT ON appointments
    FOR EACH ROW EXECUTE FUNCTION generate_confirmation_number();

-- Track appointment status changes
CREATE OR REPLACE FUNCTION track_appointment_status()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO appointment_history (appointment_id, previous_status, new_status, changed_by)
        VALUES (NEW.id, OLD.status, NEW.status, NEW.created_by);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER appointments_status_history
    AFTER UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION track_appointment_status();

-- =============================================================================
-- COMMENTS
-- =============================================================================
COMMENT ON TABLE providers IS 'Healthcare providers who can receive appointments';
COMMENT ON TABLE provider_availability IS 'Weekly recurring availability schedule';
COMMENT ON TABLE blocked_times IS 'Exceptions/overrides to regular availability';
COMMENT ON TABLE appointments IS 'Patient appointment bookings';
COMMENT ON TABLE appointment_history IS 'Audit trail of appointment status changes';

COMMENT ON COLUMN appointments.patient_id IS 'External patient identifier from EHR';
COMMENT ON COLUMN appointments.confirmation_number IS 'Patient-facing confirmation code';
COMMENT ON COLUMN provider_availability.day_of_week IS '0=Sunday, 1=Monday, ..., 6=Saturday';
```

## Checklist
- ✅ UUID primary keys (not serial)
- ✅ Audit columns (created_at, updated_at, created_by)
- ✅ ENUMs for fixed value sets
- ✅ CHECK constraints for data integrity
- ✅ Foreign keys with ON DELETE behavior
- ✅ Indexes for common query patterns
- ✅ Triggers for auto-updated fields
- ✅ Comments on tables and key columns

## Anti-patterns (DO NOT)
- ❌ Serial IDs: Use UUID for distributed systems
- ❌ Missing indexes: Always index foreign keys and query columns
- ❌ No constraints: Add CHECK constraints for business rules
- ❌ Missing audit: Include created_at/updated_at on all tables

## Output Location
`projects/{project}/db/schema.sql`

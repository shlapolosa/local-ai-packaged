---
name: sql-schema
description: Generate SQL DDL schema as JSON (transformed to SQL via script)
license: MIT
---

# SQL Schema Design Skill

You are outputting a database schema as **JSON**. Your entire response is a single JSON object.

## CRITICAL INSTRUCTIONS

1. **OUTPUT ONLY JSON** - No explanations, no markdown, no code blocks
2. **FIRST CHARACTER MUST BE `{`** - Start immediately with the JSON object
3. **VALID JSON REQUIRED** - Must be parseable by `json.loads()`
4. **NO TRAILING TEXT** - End with `}` and nothing else

## JSON Schema

```json
{
  "schema": "schema_name",
  "enums": [
    {"name": "status_type", "values": ["active", "inactive"]}
  ],
  "tables": [
    {
      "name": "table_name",
      "description": "Table description",
      "columns": [
        {"name": "id", "type": "uuid", "primaryKey": true, "default": "gen_random_uuid()"},
        {"name": "name", "type": "varchar(100)", "notNull": true},
        {"name": "status", "type": "status_type", "default": "'active'"}
      ],
      "indexes": [
        {"name": "idx_table_name", "columns": ["name"]}
      ],
      "checkConstraints": [
        {"name": "ck_positive", "expression": "amount > 0"}
      ]
    }
  ],
  "foreignKeys": [
    {"table": "orders", "column": "user_id", "references": {"table": "users", "column": "id"}, "onDelete": "CASCADE"}
  ]
}
```

## Column Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Column name (snake_case) |
| `type` | string | Data type (see types below) |
| `primaryKey` | boolean | Is primary key |
| `notNull` | boolean | NOT NULL constraint |
| `unique` | boolean | UNIQUE constraint |
| `default` | string | Default value or expression |
| `description` | string | Column comment |
| `check` | string | CHECK constraint expression |

## Data Types

| Type | PostgreSQL | Use For |
|------|------------|---------|
| `uuid` | UUID | Primary keys, IDs |
| `varchar(n)` | VARCHAR(n) | Short strings |
| `text` | TEXT | Long text |
| `integer` | INTEGER | Whole numbers |
| `bigint` | BIGINT | Large numbers |
| `decimal(p,s)` | DECIMAL(p,s) | Money, precision |
| `boolean` | BOOLEAN | True/false |
| `date` | DATE | Date only |
| `timestamp` | TIMESTAMPTZ | Date and time |
| `json` / `jsonb` | JSONB | JSON data |
| `{enum_name}` | ENUM | Custom enum type |

## Index Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Index name |
| `columns` | array | Column names |
| `unique` | boolean | Unique index |
| `where` | string | Partial index condition |

## Foreign Key Properties

| Property | Type | Description |
|----------|------|-------------|
| `table` | string | Source table |
| `column` | string | Source column |
| `references.table` | string | Target table |
| `references.column` | string | Target column |
| `onDelete` | string | CASCADE, RESTRICT, SET NULL |
| `onUpdate` | string | CASCADE, RESTRICT, SET NULL |

## Example Output

For a healthcare appointment booking system:

```json
{
  "schema": "clinic",
  "enums": [
    {"name": "appointment_status", "values": ["pending", "confirmed", "completed", "cancelled", "no_show"]},
    {"name": "visit_type", "values": ["routine", "follow_up", "urgent", "telehealth"]},
    {"name": "contact_preference", "values": ["email", "sms", "both", "none"]}
  ],
  "tables": [
    {
      "name": "providers",
      "description": "Healthcare providers (physicians, nurses)",
      "columns": [
        {"name": "id", "type": "uuid", "primaryKey": true, "default": "gen_random_uuid()"},
        {"name": "external_id", "type": "varchar(50)", "unique": true, "description": "EHR system ID"},
        {"name": "first_name", "type": "varchar(100)", "notNull": true},
        {"name": "last_name", "type": "varchar(100)", "notNull": true},
        {"name": "specialty", "type": "varchar(100)"},
        {"name": "email", "type": "varchar(255)", "unique": true},
        {"name": "is_active", "type": "boolean", "default": "true"},
        {"name": "created_at", "type": "timestamp", "default": "CURRENT_TIMESTAMP"},
        {"name": "updated_at", "type": "timestamp", "default": "CURRENT_TIMESTAMP"}
      ],
      "indexes": [
        {"name": "idx_providers_external", "columns": ["external_id"]},
        {"name": "idx_providers_active", "columns": ["is_active"], "where": "is_active = true"}
      ]
    },
    {
      "name": "provider_availability",
      "description": "Weekly recurring availability schedule",
      "columns": [
        {"name": "id", "type": "uuid", "primaryKey": true, "default": "gen_random_uuid()"},
        {"name": "provider_id", "type": "uuid", "notNull": true},
        {"name": "day_of_week", "type": "smallint", "notNull": true, "description": "0=Sunday, 6=Saturday"},
        {"name": "start_time", "type": "time", "notNull": true},
        {"name": "end_time", "type": "time", "notNull": true},
        {"name": "slot_duration_minutes", "type": "smallint", "default": "30"},
        {"name": "visit_types", "type": "visit_type[]", "default": "ARRAY['routine'::visit_type]"},
        {"name": "location", "type": "varchar(200)"},
        {"name": "is_active", "type": "boolean", "default": "true"},
        {"name": "created_at", "type": "timestamp", "default": "CURRENT_TIMESTAMP"}
      ],
      "indexes": [
        {"name": "idx_availability_provider_day", "columns": ["provider_id", "day_of_week"]}
      ],
      "checkConstraints": [
        {"name": "ck_valid_time_range", "expression": "start_time < end_time"},
        {"name": "ck_valid_day", "expression": "day_of_week BETWEEN 0 AND 6"}
      ]
    },
    {
      "name": "patients",
      "description": "Patient demographic information",
      "columns": [
        {"name": "id", "type": "uuid", "primaryKey": true, "default": "gen_random_uuid()"},
        {"name": "mrn", "type": "varchar(20)", "unique": true, "notNull": true, "description": "Medical Record Number"},
        {"name": "first_name", "type": "varchar(100)", "notNull": true},
        {"name": "last_name", "type": "varchar(100)", "notNull": true},
        {"name": "date_of_birth", "type": "date", "notNull": true},
        {"name": "email", "type": "varchar(255)"},
        {"name": "phone", "type": "varchar(20)"},
        {"name": "contact_preference", "type": "contact_preference", "default": "'email'"},
        {"name": "created_at", "type": "timestamp", "default": "CURRENT_TIMESTAMP"}
      ],
      "indexes": [
        {"name": "idx_patients_name", "columns": ["last_name", "first_name"]},
        {"name": "idx_patients_dob", "columns": ["date_of_birth"]}
      ]
    },
    {
      "name": "appointments",
      "description": "Patient appointment bookings",
      "columns": [
        {"name": "id", "type": "uuid", "primaryKey": true, "default": "gen_random_uuid()"},
        {"name": "confirmation_number", "type": "varchar(20)", "unique": true, "notNull": true},
        {"name": "provider_id", "type": "uuid", "notNull": true},
        {"name": "patient_id", "type": "uuid", "notNull": true},
        {"name": "scheduled_start", "type": "timestamp", "notNull": true},
        {"name": "scheduled_end", "type": "timestamp", "notNull": true},
        {"name": "visit_type", "type": "visit_type", "notNull": true, "default": "'routine'"},
        {"name": "status", "type": "appointment_status", "notNull": true, "default": "'pending'"},
        {"name": "reason_for_visit", "type": "text"},
        {"name": "location", "type": "varchar(200)"},
        {"name": "cancellation_reason", "type": "text"},
        {"name": "cancelled_at", "type": "timestamp"},
        {"name": "created_at", "type": "timestamp", "default": "CURRENT_TIMESTAMP"},
        {"name": "updated_at", "type": "timestamp", "default": "CURRENT_TIMESTAMP"}
      ],
      "indexes": [
        {"name": "idx_appointments_provider_date", "columns": ["provider_id", "scheduled_start"]},
        {"name": "idx_appointments_patient", "columns": ["patient_id"]},
        {"name": "idx_appointments_status", "columns": ["status"], "where": "status IN ('pending', 'confirmed')"},
        {"name": "idx_appointments_confirmation", "columns": ["confirmation_number"]}
      ],
      "checkConstraints": [
        {"name": "ck_valid_schedule", "expression": "scheduled_start < scheduled_end"}
      ]
    },
    {
      "name": "appointment_history",
      "description": "Audit trail of appointment status changes",
      "columns": [
        {"name": "id", "type": "uuid", "primaryKey": true, "default": "gen_random_uuid()"},
        {"name": "appointment_id", "type": "uuid", "notNull": true},
        {"name": "previous_status", "type": "appointment_status"},
        {"name": "new_status", "type": "appointment_status", "notNull": true},
        {"name": "changed_by", "type": "varchar(100)"},
        {"name": "change_reason", "type": "text"},
        {"name": "changed_at", "type": "timestamp", "default": "CURRENT_TIMESTAMP"}
      ],
      "indexes": [
        {"name": "idx_history_appointment", "columns": ["appointment_id", "changed_at"]}
      ]
    }
  ],
  "foreignKeys": [
    {"table": "provider_availability", "column": "provider_id", "references": {"table": "providers", "column": "id"}, "onDelete": "CASCADE"},
    {"table": "appointments", "column": "provider_id", "references": {"table": "providers", "column": "id"}, "onDelete": "RESTRICT"},
    {"table": "appointments", "column": "patient_id", "references": {"table": "patients", "column": "id"}, "onDelete": "RESTRICT"},
    {"table": "appointment_history", "column": "appointment_id", "references": {"table": "appointments", "column": "id"}, "onDelete": "CASCADE"}
  ]
}
```

## Minimum Requirements

1. **At least 3 tables** - Meaningful schema
2. **UUID primary keys** - Not serial/auto-increment
3. **Audit columns** - created_at, updated_at on main tables
4. **Foreign keys defined** - Relationships explicit
5. **Indexes for queries** - On foreign keys and search columns

## Naming Conventions

- Tables: `snake_case`, plural (`users`, `appointments`)
- Columns: `snake_case` (`first_name`, `created_at`)
- Indexes: `idx_{table}_{column}` (`idx_users_email`)
- Foreign keys: `fk_{table}_{column}` (`fk_orders_user_id`)
- Constraints: `ck_{table}_{rule}` (`ck_orders_positive_amount`)

## Post-Processing

The JSON output will be transformed to SQL DDL using:
```bash
python scripts/json-to-sql.py input.json output.sql
```

This produces PostgreSQL-compatible DDL with:
- CREATE SCHEMA, ENUM, TABLE statements
- Indexes, foreign keys, constraints
- Comments on tables and columns

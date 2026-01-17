#!/usr/bin/env python3
"""
json-to-sql.py - Transform LLM JSON output to SQL DDL

This script takes JSON input describing database tables and generates
PostgreSQL-compatible SQL DDL statements.

Usage:
    python json-to-sql.py input.json output.sql
    cat input.json | python json-to-sql.py - output.sql
    echo '{"tables": [...]}' | python json-to-sql.py

JSON Schema:
{
    "schema": "public",
    "tables": [
        {
            "name": "users",
            "description": "Application users",
            "columns": [
                {"name": "id", "type": "uuid", "primaryKey": true, "default": "gen_random_uuid()"},
                {"name": "email", "type": "varchar(255)", "unique": true, "notNull": true},
                {"name": "created_at", "type": "timestamp", "default": "CURRENT_TIMESTAMP"}
            ],
            "indexes": [
                {"name": "idx_users_email", "columns": ["email"], "unique": true}
            ]
        }
    ],
    "foreignKeys": [
        {"table": "orders", "column": "user_id", "references": {"table": "users", "column": "id"}, "onDelete": "CASCADE"}
    ],
    "enums": [
        {"name": "status_type", "values": ["pending", "active", "inactive"]}
    ]
}
"""

import json
import sys
import argparse
from typing import Dict, Any, List, Optional
from datetime import datetime


# Type mapping from common types to PostgreSQL types
TYPE_MAPPING = {
    # Standard types
    "uuid": "UUID",
    "string": "VARCHAR(255)",
    "text": "TEXT",
    "integer": "INTEGER",
    "int": "INTEGER",
    "bigint": "BIGINT",
    "smallint": "SMALLINT",
    "decimal": "DECIMAL(10,2)",
    "numeric": "NUMERIC",
    "float": "FLOAT",
    "double": "DOUBLE PRECISION",
    "boolean": "BOOLEAN",
    "bool": "BOOLEAN",
    "date": "DATE",
    "time": "TIME",
    "timestamp": "TIMESTAMP WITH TIME ZONE",
    "datetime": "TIMESTAMP WITH TIME ZONE",
    "json": "JSONB",
    "jsonb": "JSONB",
    "array": "TEXT[]",
    "bytea": "BYTEA",
    "binary": "BYTEA",

    # Shortcuts
    "varchar": "VARCHAR(255)",
    "char": "CHAR(1)",
}


def map_type(type_str: str) -> str:
    """Map JSON type to PostgreSQL type."""
    type_lower = type_str.lower()

    # Direct mapping
    if type_lower in TYPE_MAPPING:
        return TYPE_MAPPING[type_lower]

    # Check for parameterized types (varchar(100), decimal(10,2), etc.)
    if "(" in type_str:
        base_type = type_str.split("(")[0].lower()
        if base_type in ["varchar", "char", "decimal", "numeric"]:
            return type_str.upper()

    # Return as-is if not found (might be custom type or enum)
    return type_str.upper()


def generate_column_sql(column: Dict[str, Any]) -> str:
    """Generate SQL for a single column definition."""
    parts = [f'"{column["name"]}"']

    # Type
    col_type = map_type(column.get("type", "varchar"))
    parts.append(col_type)

    # Primary key
    if column.get("primaryKey"):
        parts.append("PRIMARY KEY")

    # Not null (unless primary key which is implicitly not null)
    if column.get("notNull") and not column.get("primaryKey"):
        parts.append("NOT NULL")

    # Unique
    if column.get("unique") and not column.get("primaryKey"):
        parts.append("UNIQUE")

    # Default
    if column.get("default") is not None:
        default = column["default"]
        if isinstance(default, str):
            # Check if it's a function call
            if "(" in default and ")" in default:
                parts.append(f"DEFAULT {default}")
            elif default.upper() in ["CURRENT_TIMESTAMP", "NOW()", "TRUE", "FALSE", "NULL"]:
                parts.append(f"DEFAULT {default}")
            else:
                parts.append(f"DEFAULT '{default}'")
        elif isinstance(default, bool):
            parts.append(f"DEFAULT {str(default).upper()}")
        elif isinstance(default, (int, float)):
            parts.append(f"DEFAULT {default}")

    # Check constraint
    if column.get("check"):
        parts.append(f'CHECK ({column["check"]})')

    return "    " + " ".join(parts)


def generate_index_sql(table_name: str, index: Dict[str, Any], schema: str = "public") -> str:
    """Generate SQL for index creation."""
    index_name = index.get("name", f"idx_{table_name}_{'_'.join(index['columns'])}")
    columns = ", ".join([f'"{c}"' for c in index["columns"]])

    unique = "UNIQUE " if index.get("unique") else ""
    method = index.get("method", "btree").upper()

    # Handle partial indexes
    where_clause = ""
    if index.get("where"):
        where_clause = f' WHERE {index["where"]}'

    return f'CREATE {unique}INDEX "{index_name}" ON "{schema}"."{table_name}" USING {method} ({columns}){where_clause};'


def generate_foreign_key_sql(fk: Dict[str, Any], schema: str = "public") -> str:
    """Generate SQL for foreign key constraint."""
    table = fk["table"]
    column = fk["column"]
    ref_table = fk["references"]["table"]
    ref_column = fk["references"]["column"]

    constraint_name = fk.get("name", f"fk_{table}_{column}")

    on_delete = fk.get("onDelete", "NO ACTION").upper()
    on_update = fk.get("onUpdate", "NO ACTION").upper()

    return f'''ALTER TABLE "{schema}"."{table}"
    ADD CONSTRAINT "{constraint_name}"
    FOREIGN KEY ("{column}") REFERENCES "{schema}"."{ref_table}"("{ref_column}")
    ON DELETE {on_delete}
    ON UPDATE {on_update};'''


def generate_enum_sql(enum: Dict[str, Any], schema: str = "public") -> str:
    """Generate SQL for enum type creation."""
    name = enum["name"]
    values = ", ".join([f"'{v}'" for v in enum["values"]])
    return f'CREATE TYPE "{schema}"."{name}" AS ENUM ({values});'


def transform_to_sql(data: Dict[str, Any]) -> str:
    """Transform JSON to SQL DDL."""
    schema = data.get("schema", "public")
    sql_parts = []

    # Header comment
    sql_parts.append(f"-- Generated SQL DDL")
    sql_parts.append(f"-- Schema: {schema}")
    sql_parts.append(f"-- Generated at: {datetime.now().isoformat()}")
    sql_parts.append("")

    # Create schema if not public
    if schema != "public":
        sql_parts.append(f'CREATE SCHEMA IF NOT EXISTS "{schema}";')
        sql_parts.append("")

    # Create enums first (before tables that might use them)
    enums = data.get("enums", [])
    if enums:
        sql_parts.append("-- Enum Types")
        sql_parts.append("-- =========")
        for enum in enums:
            sql_parts.append(generate_enum_sql(enum, schema))
        sql_parts.append("")

    # Create tables
    tables = data.get("tables", [])
    if tables:
        sql_parts.append("-- Tables")
        sql_parts.append("-- ======")
        sql_parts.append("")

    for table in tables:
        table_name = table["name"]
        description = table.get("description", "")

        # Table comment
        if description:
            sql_parts.append(f"-- {description}")

        # CREATE TABLE
        sql_parts.append(f'CREATE TABLE "{schema}"."{table_name}" (')

        # Columns
        columns = table.get("columns", [])
        column_sqls = [generate_column_sql(col) for col in columns]

        # Composite primary key
        pk_columns = [col["name"] for col in columns if col.get("primaryKey")]
        if len(pk_columns) > 1:
            # Remove PRIMARY KEY from individual columns and add composite
            column_sqls = [sql.replace(" PRIMARY KEY", "") for sql in column_sqls]
            pk_sql = f'    PRIMARY KEY ({", ".join([f"{c}" for c in pk_columns])})'
            column_sqls.append(pk_sql)

        # Unique constraints (multi-column)
        unique_constraints = table.get("uniqueConstraints", [])
        for uc in unique_constraints:
            cols = ", ".join([f'"{c}"' for c in uc["columns"]])
            uc_name = uc.get("name", f"uq_{table_name}_{'_'.join(uc['columns'])}")
            column_sqls.append(f'    CONSTRAINT "{uc_name}" UNIQUE ({cols})')

        # Check constraints
        check_constraints = table.get("checkConstraints", [])
        for cc in check_constraints:
            cc_name = cc.get("name", f"ck_{table_name}")
            column_sqls.append(f'    CONSTRAINT "{cc_name}" CHECK ({cc["expression"]})')

        sql_parts.append(",\n".join(column_sqls))
        sql_parts.append(");")
        sql_parts.append("")

        # Table comment
        if description:
            escaped_desc = description.replace("'", "''")
            sql_parts.append(f'COMMENT ON TABLE "{schema}"."{table_name}" IS \'{escaped_desc}\';')
            sql_parts.append("")

        # Column comments
        for col in columns:
            if col.get("description"):
                escaped_col_desc = col["description"].replace("'", "''")
                sql_parts.append(f'COMMENT ON COLUMN "{schema}"."{table_name}"."{col["name"]}" IS \'{escaped_col_desc}\';')

        # Indexes
        indexes = table.get("indexes", [])
        for index in indexes:
            sql_parts.append(generate_index_sql(table_name, index, schema))

        sql_parts.append("")

    # Foreign keys (after all tables created)
    foreign_keys = data.get("foreignKeys", [])
    if foreign_keys:
        sql_parts.append("-- Foreign Keys")
        sql_parts.append("-- ============")
        for fk in foreign_keys:
            sql_parts.append(generate_foreign_key_sql(fk, schema))
            sql_parts.append("")

    return "\n".join(sql_parts)


def main():
    parser = argparse.ArgumentParser(
        description="Transform LLM JSON output to SQL DDL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("input", nargs="?", default="-",
                        help="Input JSON file (use - for stdin)")
    parser.add_argument("output", nargs="?", default=None,
                        help="Output SQL file (prints to stdout if not specified)")

    args = parser.parse_args()

    # Read input
    if args.input == "-":
        json_input = sys.stdin.read()
    else:
        with open(args.input, 'r') as f:
            json_input = f.read()

    # Parse JSON
    try:
        data = json.loads(json_input)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Transform
    sql_output = transform_to_sql(data)

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(sql_output)
        print(f"SQL written to {args.output}", file=sys.stderr)
    else:
        print(sql_output)


if __name__ == "__main__":
    main()

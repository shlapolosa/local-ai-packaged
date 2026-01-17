#!/usr/bin/env python3
"""
json-to-openapi.py - Transform LLM JSON output to OpenAPI 3.1 YAML

This script takes JSON input describing an API and generates valid
OpenAPI 3.1 specification in YAML format.

Usage:
    python json-to-openapi.py input.json output.yaml
    cat input.json | python json-to-openapi.py - output.yaml
    echo '{"title": "My API", ...}' | python json-to-openapi.py

JSON Schema:
{
    "title": "API Title",
    "description": "API Description",
    "version": "1.0.0",
    "servers": [{"url": "https://api.example.com", "description": "Production"}],
    "tags": [{"name": "users", "description": "User operations"}],
    "paths": [
        {
            "path": "/users",
            "method": "get",
            "operationId": "listUsers",
            "summary": "List all users",
            "tags": ["users"],
            "parameters": [{"name": "limit", "in": "query", "type": "integer"}],
            "responses": [
                {"status": "200", "description": "Success", "schema": "UserList"}
            ]
        }
    ],
    "schemas": [
        {
            "name": "User",
            "type": "object",
            "description": "A user in the system",
            "properties": [
                {"name": "id", "type": "string", "format": "uuid", "description": "User ID"},
                {"name": "name", "type": "string", "description": "User name"}
            ],
            "required": ["id", "name"]
        }
    ]
}
"""

import json
import sys
import argparse
from typing import Dict, Any, List
import yaml

# Ensure proper YAML output
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper


def transform_to_openapi(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform JSON to OpenAPI 3.1 structure."""

    openapi = {
        "openapi": "3.1.0",
        "info": {
            "title": data.get("title", "API"),
            "description": data.get("description", ""),
            "version": data.get("version", "1.0.0"),
        },
    }

    # Add servers
    servers = data.get("servers", [])
    if servers:
        openapi["servers"] = servers
    else:
        openapi["servers"] = [{"url": "https://api.example.com/v1", "description": "API Server"}]

    # Add tags
    tags = data.get("tags", [])
    if tags:
        openapi["tags"] = tags

    # Process paths
    paths = {}
    for path_item in data.get("paths", []):
        path = path_item.get("path", "/")
        method = path_item.get("method", "get").lower()

        if path not in paths:
            paths[path] = {}

        operation = {
            "operationId": path_item.get("operationId", f"{method}_{path.replace('/', '_')}"),
            "summary": path_item.get("summary", ""),
        }

        if path_item.get("description"):
            operation["description"] = path_item["description"]

        if path_item.get("tags"):
            operation["tags"] = path_item["tags"]

        # Parameters
        params = path_item.get("parameters", [])
        if params:
            operation["parameters"] = []
            for param in params:
                param_obj = {
                    "name": param.get("name", "param"),
                    "in": param.get("in", "query"),
                }
                if param.get("description"):
                    param_obj["description"] = param["description"]
                if param.get("required"):
                    param_obj["required"] = param["required"]

                # Schema
                param_schema = {"type": param.get("type", "string")}
                if param.get("format"):
                    param_schema["format"] = param["format"]
                if param.get("enum"):
                    param_schema["enum"] = param["enum"]
                if param.get("default") is not None:
                    param_schema["default"] = param["default"]

                param_obj["schema"] = param_schema
                operation["parameters"].append(param_obj)

        # Request body
        if path_item.get("requestBody"):
            rb = path_item["requestBody"]
            request_body = {
                "required": rb.get("required", True),
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{rb.get('schema', 'Object')}"}
                    }
                }
            }
            if rb.get("description"):
                request_body["description"] = rb["description"]
            operation["requestBody"] = request_body

        # Responses
        responses = {}
        for resp in path_item.get("responses", []):
            status = str(resp.get("status", "200"))
            resp_obj = {"description": resp.get("description", "Response")}

            if resp.get("schema"):
                resp_obj["content"] = {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{resp['schema']}"}
                    }
                }

            responses[status] = resp_obj

        # Default error responses if not specified
        if "400" not in responses:
            responses["400"] = {"description": "Bad Request"}
        if "500" not in responses:
            responses["500"] = {"description": "Internal Server Error"}

        operation["responses"] = responses

        paths[path][method] = operation

    openapi["paths"] = paths

    # Process schemas/components
    schemas = {}
    for schema_item in data.get("schemas", []):
        name = schema_item.get("name", "Object")
        schema_obj = {
            "type": schema_item.get("type", "object"),
        }

        if schema_item.get("description"):
            schema_obj["description"] = schema_item["description"]

        # Properties
        if schema_item.get("properties"):
            props = {}
            for prop in schema_item["properties"]:
                prop_name = prop.get("name", "property")
                prop_obj = {"type": prop.get("type", "string")}

                if prop.get("format"):
                    prop_obj["format"] = prop["format"]
                if prop.get("description"):
                    prop_obj["description"] = prop["description"]
                if prop.get("enum"):
                    prop_obj["enum"] = prop["enum"]
                if prop.get("default") is not None:
                    prop_obj["default"] = prop["default"]
                if prop.get("items"):
                    prop_obj["items"] = prop["items"]
                if prop.get("$ref"):
                    prop_obj = {"$ref": f"#/components/schemas/{prop['$ref']}"}

                props[prop_name] = prop_obj

            schema_obj["properties"] = props

        # Required fields
        if schema_item.get("required"):
            schema_obj["required"] = schema_item["required"]

        schemas[name] = schema_obj

    if schemas:
        openapi["components"] = {"schemas": schemas}

    return openapi


def generate_yaml(openapi: Dict[str, Any]) -> str:
    """Generate YAML from OpenAPI dict."""

    # Custom representer for multiline strings
    def str_representer(dumper, data):
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    yaml.add_representer(str, str_representer, Dumper=Dumper)

    return yaml.dump(openapi, Dumper=Dumper, default_flow_style=False, sort_keys=False, allow_unicode=True)


def main():
    parser = argparse.ArgumentParser(
        description="Transform LLM JSON output to OpenAPI 3.1 YAML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("input", nargs="?", default="-",
                        help="Input JSON file (use - for stdin)")
    parser.add_argument("output", nargs="?", default=None,
                        help="Output YAML file (prints to stdout if not specified)")

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
    openapi = transform_to_openapi(data)

    # Generate YAML
    yaml_output = generate_yaml(openapi)

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(yaml_output)
        print(f"OpenAPI spec written to {args.output}", file=sys.stderr)
    else:
        print(yaml_output)


if __name__ == "__main__":
    main()

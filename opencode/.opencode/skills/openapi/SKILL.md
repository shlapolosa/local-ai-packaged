---
name: openapi
description: Generate OpenAPI 3.1 specifications as JSON (transformed to YAML via script)
license: MIT
---

# OpenAPI Design Skill

You are outputting an OpenAPI specification as **JSON**. Your entire response is a single JSON object.

## CRITICAL INSTRUCTIONS

1. **OUTPUT ONLY JSON** - No explanations, no markdown, no code blocks
2. **FIRST CHARACTER MUST BE `{`** - Start immediately with the JSON object
3. **VALID JSON REQUIRED** - Must be parseable by `json.loads()`
4. **NO TRAILING TEXT** - End with `}` and nothing else

## JSON Schema

```json
{
  "title": "API Title",
  "description": "API description",
  "version": "1.0.0",
  "servers": [
    {"url": "https://api.example.com/v1", "description": "Production"}
  ],
  "tags": [
    {"name": "resource", "description": "Resource operations"}
  ],
  "paths": [
    {
      "path": "/resources",
      "method": "get",
      "operationId": "listResources",
      "summary": "List resources",
      "description": "Optional longer description",
      "tags": ["resource"],
      "parameters": [
        {"name": "limit", "in": "query", "type": "integer", "default": 20}
      ],
      "responses": [
        {"status": "200", "description": "Success", "schema": "ResourceList"}
      ]
    },
    {
      "path": "/resources",
      "method": "post",
      "operationId": "createResource",
      "summary": "Create resource",
      "tags": ["resource"],
      "requestBody": {"schema": "ResourceCreate", "required": true},
      "responses": [
        {"status": "201", "description": "Created", "schema": "Resource"}
      ]
    }
  ],
  "schemas": [
    {
      "name": "Resource",
      "type": "object",
      "description": "A resource",
      "properties": [
        {"name": "id", "type": "string", "format": "uuid"},
        {"name": "name", "type": "string"}
      ],
      "required": ["id", "name"]
    }
  ]
}
```

## Path Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | Yes | URL path (e.g., `/users`, `/users/{id}`) |
| `method` | string | Yes | HTTP method (get, post, put, patch, delete) |
| `operationId` | string | Yes | Unique operation ID (camelCase) |
| `summary` | string | Yes | Short description |
| `description` | string | No | Longer description |
| `tags` | array | No | Tag names for grouping |
| `parameters` | array | No | Path/query/header parameters |
| `requestBody` | object | No | Request body schema (for POST/PUT/PATCH) |
| `responses` | array | Yes | Response definitions |

## Parameter Structure

```json
{
  "name": "paramName",
  "in": "query|path|header",
  "type": "string|integer|boolean|array",
  "format": "uuid|date|date-time|email",
  "required": true,
  "description": "Parameter description",
  "enum": ["value1", "value2"],
  "default": "defaultValue"
}
```

## Response Structure

```json
{
  "status": "200|201|204|400|401|404|409|500",
  "description": "Response description",
  "schema": "SchemaName"
}
```

## Schema Structure

```json
{
  "name": "SchemaName",
  "type": "object|array",
  "description": "Schema description",
  "properties": [
    {"name": "fieldName", "type": "string", "format": "uuid", "description": "Field desc"},
    {"name": "items", "type": "array", "items": {"$ref": "OtherSchema"}}
  ],
  "required": ["field1", "field2"]
}
```

## Example Output

For a healthcare appointment booking API:

```json
{
  "title": "Healthcare Appointment Booking API",
  "description": "API for patient self-scheduling appointments with healthcare providers",
  "version": "1.0.0",
  "servers": [
    {"url": "https://api.clinic.com/v1", "description": "Production"},
    {"url": "https://staging.clinic.com/v1", "description": "Staging"}
  ],
  "tags": [
    {"name": "slots", "description": "Available appointment slots"},
    {"name": "appointments", "description": "Appointment management"},
    {"name": "providers", "description": "Healthcare providers"}
  ],
  "paths": [
    {
      "path": "/slots",
      "method": "get",
      "operationId": "searchSlots",
      "summary": "Search available appointment slots",
      "tags": ["slots"],
      "parameters": [
        {"name": "providerId", "in": "query", "type": "string", "format": "uuid", "description": "Filter by provider"},
        {"name": "startDate", "in": "query", "type": "string", "format": "date", "required": true},
        {"name": "endDate", "in": "query", "type": "string", "format": "date", "required": true},
        {"name": "visitType", "in": "query", "type": "string", "enum": ["routine", "follow-up", "urgent"]},
        {"name": "limit", "in": "query", "type": "integer", "default": 20}
      ],
      "responses": [
        {"status": "200", "description": "Available slots", "schema": "SlotList"}
      ]
    },
    {
      "path": "/appointments",
      "method": "post",
      "operationId": "createAppointment",
      "summary": "Book an appointment",
      "tags": ["appointments"],
      "requestBody": {"schema": "AppointmentCreate", "required": true},
      "responses": [
        {"status": "201", "description": "Appointment created", "schema": "Appointment"},
        {"status": "409", "description": "Slot no longer available"}
      ]
    },
    {
      "path": "/appointments/{id}",
      "method": "get",
      "operationId": "getAppointment",
      "summary": "Get appointment details",
      "tags": ["appointments"],
      "parameters": [
        {"name": "id", "in": "path", "type": "string", "format": "uuid", "required": true}
      ],
      "responses": [
        {"status": "200", "description": "Appointment details", "schema": "Appointment"},
        {"status": "404", "description": "Not found"}
      ]
    },
    {
      "path": "/appointments/{id}",
      "method": "delete",
      "operationId": "cancelAppointment",
      "summary": "Cancel an appointment",
      "tags": ["appointments"],
      "parameters": [
        {"name": "id", "in": "path", "type": "string", "format": "uuid", "required": true},
        {"name": "reason", "in": "query", "type": "string", "description": "Cancellation reason"}
      ],
      "responses": [
        {"status": "204", "description": "Cancelled"},
        {"status": "404", "description": "Not found"}
      ]
    },
    {
      "path": "/providers/{providerId}/availability",
      "method": "get",
      "operationId": "getProviderAvailability",
      "summary": "Get provider's available time slots",
      "tags": ["providers"],
      "parameters": [
        {"name": "providerId", "in": "path", "type": "string", "format": "uuid", "required": true},
        {"name": "date", "in": "query", "type": "string", "format": "date", "required": true}
      ],
      "responses": [
        {"status": "200", "description": "Available slots", "schema": "TimeSlotList"}
      ]
    }
  ],
  "schemas": [
    {
      "name": "Slot",
      "type": "object",
      "description": "An available appointment slot",
      "properties": [
        {"name": "id", "type": "string", "format": "uuid"},
        {"name": "providerId", "type": "string", "format": "uuid"},
        {"name": "providerName", "type": "string"},
        {"name": "startTime", "type": "string", "format": "date-time"},
        {"name": "endTime", "type": "string", "format": "date-time"},
        {"name": "visitType", "type": "string", "enum": ["routine", "follow-up", "urgent"]},
        {"name": "location", "type": "string"}
      ],
      "required": ["id", "providerId", "startTime", "endTime"]
    },
    {
      "name": "SlotList",
      "type": "object",
      "properties": [
        {"name": "data", "type": "array", "items": {"$ref": "Slot"}},
        {"name": "total", "type": "integer"},
        {"name": "limit", "type": "integer"},
        {"name": "offset", "type": "integer"}
      ]
    },
    {
      "name": "AppointmentCreate",
      "type": "object",
      "description": "Request body for creating an appointment",
      "properties": [
        {"name": "slotId", "type": "string", "format": "uuid"},
        {"name": "patientId", "type": "string"},
        {"name": "reasonForVisit", "type": "string"},
        {"name": "contactPreference", "type": "string", "enum": ["email", "sms", "both"], "default": "email"}
      ],
      "required": ["slotId", "patientId"]
    },
    {
      "name": "Appointment",
      "type": "object",
      "description": "A booked appointment",
      "properties": [
        {"name": "id", "type": "string", "format": "uuid"},
        {"name": "confirmationNumber", "type": "string"},
        {"name": "status", "type": "string", "enum": ["confirmed", "cancelled", "completed", "no-show"]},
        {"name": "slotId", "type": "string", "format": "uuid"},
        {"name": "patientId", "type": "string"},
        {"name": "reasonForVisit", "type": "string"},
        {"name": "createdAt", "type": "string", "format": "date-time"}
      ],
      "required": ["id", "confirmationNumber", "status", "slotId", "patientId"]
    },
    {
      "name": "TimeSlotList",
      "type": "object",
      "properties": [
        {"name": "providerId", "type": "string", "format": "uuid"},
        {"name": "date", "type": "string", "format": "date"},
        {"name": "slots", "type": "array", "items": {"$ref": "Slot"}}
      ]
    }
  ]
}
```

## Minimum Requirements

1. **At least 3 endpoints** - Meaningful API needs multiple operations
2. **At least 2 schemas** - Reusable data types
3. **operationId for every path** - Unique, camelCase
4. **Responses for every path** - At least success response
5. **Required fields marked** - In schema definitions

## Post-Processing

The JSON output will be transformed to OpenAPI YAML using:
```bash
python scripts/json-to-openapi.py input.json output.yaml
```

This produces valid OpenAPI 3.1 YAML for:
- API documentation generators (Swagger UI, Redoc)
- Code generators (openapi-generator)
- Testing tools (Postman, Insomnia)

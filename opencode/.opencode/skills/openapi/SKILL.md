---
name: openapi
description: Generate OpenAPI 3.1 specifications from architecture and requirements
license: MIT
---

# OpenAPI Design Skill

## CRITICAL INSTRUCTIONS
1. **DO NOT** ask the user any questions
2. **DO NOT** request additional information
3. **DO NOT** add preamble text like "Based on the provided..." or "Here is the code..."
4. **DO NOT** wrap output in code blocks (no ```) - output raw YAML directly
5. **DO NOT** generate Python/JavaScript code to output the YAML
6. **DO NOT** add extra BRD/PRD content after the OpenAPI spec - only output the spec
7. **USE THE USER'S INPUT** - extract endpoints, schemas from THEIR message
8. **STAY ON TOPIC** - the API must be about the user's project (appointments, slots, providers, etc)
9. **IMMEDIATELY** output the OpenAPI YAML (not code or explanation)
10. Your **FIRST LINE** must be `openapi: 3.1.0` - start the YAML directly

**IMPORTANT**: Output ONLY raw OpenAPI YAML. No preamble. No code blocks. First line is `openapi: 3.1.0`.

## Output Format
Output MUST be valid YAML starting with `openapi: 3.1.0`.

## Example Output

```yaml
openapi: 3.1.0
info:
  title: Patient Appointment API
  version: 1.0.0
  description: API for patient self-scheduling appointments
  contact:
    name: API Support
    email: api-support@clinic.com

servers:
  - url: https://api.clinic.com/v1
    description: Production
  - url: https://api.staging.clinic.com/v1
    description: Staging

tags:
  - name: slots
    description: Available appointment slots
  - name: appointments
    description: Appointment management
  - name: providers
    description: Healthcare providers

paths:
  /slots:
    get:
      operationId: searchSlots
      summary: Search available appointment slots
      tags: [slots]
      parameters:
        - name: providerId
          in: query
          description: Filter by specific provider
          schema:
            type: string
            format: uuid
        - name: startDate
          in: query
          required: true
          description: Start of date range (ISO 8601)
          schema:
            type: string
            format: date
        - name: endDate
          in: query
          required: true
          schema:
            type: string
            format: date
        - name: visitType
          in: query
          schema:
            type: string
            enum: [routine, follow-up, urgent]
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
      responses:
        '200':
          description: Available slots found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SlotList'
              example:
                data:
                  - id: "550e8400-e29b-41d4-a716-446655440000"
                    providerId: "123e4567-e89b-12d3-a456-426614174000"
                    providerName: "Dr. Smith"
                    startTime: "2024-01-15T09:00:00Z"
                    endTime: "2024-01-15T09:30:00Z"
                    visitType: "routine"
                    location: "Main Clinic, Room 101"
                total: 45
                limit: 20
                offset: 0
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /appointments:
    post:
      operationId: createAppointment
      summary: Book an appointment
      tags: [appointments]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AppointmentCreate'
            example:
              slotId: "550e8400-e29b-41d4-a716-446655440000"
              patientId: "patient-123"
              reasonForVisit: "Annual checkup"
              contactPreference: "email"
      responses:
        '201':
          description: Appointment created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Appointment'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '409':
          description: Slot no longer available
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /appointments/{id}:
    get:
      operationId: getAppointment
      summary: Get appointment details
      tags: [appointments]
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Appointment details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Appointment'
        '404':
          $ref: '#/components/responses/NotFound'

    delete:
      operationId: cancelAppointment
      summary: Cancel an appointment
      tags: [appointments]
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: reason
          in: query
          description: Cancellation reason
          schema:
            type: string
      responses:
        '204':
          description: Appointment cancelled
        '404':
          $ref: '#/components/responses/NotFound'
        '409':
          description: Cannot cancel (too close to appointment time)

components:
  schemas:
    Slot:
      type: object
      required: [id, providerId, startTime, endTime]
      properties:
        id:
          type: string
          format: uuid
        providerId:
          type: string
          format: uuid
        providerName:
          type: string
        startTime:
          type: string
          format: date-time
        endTime:
          type: string
          format: date-time
        visitType:
          type: string
          enum: [routine, follow-up, urgent]
        location:
          type: string

    SlotList:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/Slot'
        total:
          type: integer
        limit:
          type: integer
        offset:
          type: integer

    AppointmentCreate:
      type: object
      required: [slotId, patientId]
      properties:
        slotId:
          type: string
          format: uuid
        patientId:
          type: string
        reasonForVisit:
          type: string
          maxLength: 500
        contactPreference:
          type: string
          enum: [email, sms, both]
          default: email

    Appointment:
      type: object
      properties:
        id:
          type: string
          format: uuid
        confirmationNumber:
          type: string
          pattern: '^APT-[A-Z0-9]{8}$'
        status:
          type: string
          enum: [confirmed, cancelled, completed, no-show]
        slot:
          $ref: '#/components/schemas/Slot'
        patientId:
          type: string
        reasonForVisit:
          type: string
        createdAt:
          type: string
          format: date-time

    Error:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: object

  responses:
    BadRequest:
      description: Invalid request parameters
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

## Checklist
- ✅ Every endpoint has `operationId` (camelCase)
- ✅ Request/response examples included
- ✅ Error responses defined (400, 401, 404, 409, 500)
- ✅ Pagination for list endpoints (limit, offset, total)
- ✅ UUID format for IDs
- ✅ ISO 8601 for dates/times
- ✅ Reusable schemas in components
- ✅ Tags for grouping

## Anti-patterns (DO NOT)
- ❌ Missing operationId: Every operation needs unique ID
- ❌ No examples: Include realistic example values
- ❌ Inline schemas: Use $ref for reusability
- ❌ Missing error responses: Always include 400, 401, 404

## Output Location
`projects/{project}/api/openapi.yaml`

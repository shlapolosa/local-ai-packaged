# Business Analyst Output Schema

This document defines the required JSON output schema for the Pre-Feasibility Business Analyst agent.

## Output Requirements

- Output MUST be valid JSON only
- NO markdown, explanations, or conversational text
- Response MUST start with `{` and end with `}`
- All required fields must be present

## JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BAAnalysisOutput",
  "type": "object",
  "required": ["goals", "stories", "gaps", "analysisMetadata"],
  "properties": {
    "goals": {
      "type": "array",
      "description": "Business goals derived from requirements",
      "items": {
        "type": "object",
        "required": ["id", "description", "type", "category"],
        "properties": {
          "id": { "type": "string", "pattern": "^G-[0-9]{3}$" },
          "description": { "type": "string" },
          "type": { "type": "string", "enum": ["explicit", "derived"] },
          "source": { "type": "string" },
          "category": {
            "type": "string",
            "enum": ["patient_outcome", "operational", "compliance", "integration", "business"]
          },
          "smartValidation": {
            "type": "object",
            "properties": {
              "specific": { "type": "boolean" },
              "measurable": { "type": "boolean" },
              "achievable": { "type": "string", "enum": ["unknown", "yes", "no", "needs_validation"] },
              "relevant": { "type": "boolean" },
              "timeBound": { "type": "boolean" }
            }
          },
          "dependencies": { "type": "array", "items": { "type": "string" } },
          "conflicts": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "features": {
      "type": "array",
      "description": "Features grouping related stories (for product/feature entry level)",
      "items": {
        "type": "object",
        "required": ["id", "title"],
        "properties": {
          "id": { "type": "string", "pattern": "^F-[0-9]{3}$" },
          "title": { "type": "string" },
          "description": { "type": "string" },
          "stories": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "stories": {
      "type": "array",
      "description": "User stories with acceptance criteria",
      "items": {
        "type": "object",
        "required": ["id", "title", "asA", "iWant", "soThat", "priority"],
        "properties": {
          "id": { "type": "string", "pattern": "^S-[0-9]{3}$" },
          "featureId": { "type": "string" },
          "title": { "type": "string" },
          "asA": { "type": "string" },
          "iWant": { "type": "string" },
          "soThat": { "type": "string" },
          "acceptanceCriteria": {
            "type": "array",
            "items": { "type": "string" }
          },
          "linkedGoals": { "type": "array", "items": { "type": "string" } },
          "linkedRequirements": { "type": "array", "items": { "type": "string" } },
          "priority": { "type": "string", "enum": ["must", "should", "could", "wont"] },
          "notes": { "type": "string" }
        }
      }
    },
    "gaps": {
      "type": "object",
      "description": "Identified gaps in requirements",
      "properties": {
        "unaddressedGoals": { "type": "array", "items": { "type": "string" } },
        "orphanRequirements": { "type": "array", "items": { "type": "string" } },
        "ambiguousRequirements": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "requirement": { "type": "string" },
              "issue": { "type": "string" },
              "clarificationNeeded": { "type": "string" }
            }
          }
        },
        "missingRequirements": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "area": { "type": "string" },
              "description": { "type": "string" },
              "severity": { "type": "string", "enum": ["critical", "high", "medium", "low"] }
            }
          }
        },
        "conflictingRequirements": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "requirement1": { "type": "string" },
              "requirement2": { "type": "string" },
              "conflict": { "type": "string" }
            }
          }
        }
      }
    },
    "healthcareConsiderations": {
      "type": "array",
      "description": "Healthcare-specific considerations",
      "items": {
        "type": "object",
        "required": ["type", "description"],
        "properties": {
          "type": {
            "type": "string",
            "enum": ["regulatory", "consent", "data", "integration", "clinical_safety"]
          },
          "description": { "type": "string" },
          "impactedStories": { "type": "array", "items": { "type": "string" } },
          "recommendation": { "type": "string" }
        }
      }
    },
    "analysisMetadata": {
      "type": "object",
      "required": ["goalsCount", "storiesCount", "completedAt"],
      "properties": {
        "goalsCount": { "type": "integer" },
        "featuresCount": { "type": "integer" },
        "storiesCount": { "type": "integer" },
        "criticalGapsCount": { "type": "integer" },
        "completedAt": { "type": "string", "format": "date-time" }
      }
    }
  }
}
```

## Example Output

```json
{
  "goals": [
    {
      "id": "G-001",
      "description": "Enable patients to check-in electronically to reduce wait times",
      "type": "derived",
      "source": "Inferred from 'Build a patient check-in kiosk' requirement",
      "category": "patient_outcome",
      "smartValidation": {
        "specific": true,
        "measurable": true,
        "achievable": "yes",
        "relevant": true,
        "timeBound": false
      },
      "dependencies": [],
      "conflicts": []
    }
  ],
  "features": [
    {
      "id": "F-001",
      "title": "Patient Self-Service Check-in",
      "description": "Allow patients to check themselves in via kiosk",
      "stories": ["S-001", "S-002"]
    }
  ],
  "stories": [
    {
      "id": "S-001",
      "featureId": "F-001",
      "title": "Patient identification at kiosk",
      "asA": "Patient",
      "iWant": "to identify myself using my Emirates ID or phone number",
      "soThat": "the system can retrieve my appointment details",
      "acceptanceCriteria": [
        "Given a patient with an appointment, when they scan Emirates ID, then their details are displayed",
        "Given an invalid ID, when scanned, then an error message is shown"
      ],
      "linkedGoals": ["G-001"],
      "linkedRequirements": ["REQ-001"],
      "priority": "must",
      "notes": ""
    }
  ],
  "gaps": {
    "unaddressedGoals": [],
    "orphanRequirements": [],
    "ambiguousRequirements": [],
    "missingRequirements": [
      {
        "area": "Security",
        "description": "No authentication/authorization requirements specified",
        "severity": "high"
      }
    ],
    "conflictingRequirements": []
  },
  "healthcareConsiderations": [
    {
      "type": "data",
      "description": "Patient identification requires handling of PII/PHI",
      "impactedStories": ["S-001"],
      "recommendation": "Implement data minimization and ensure ADHICS compliance"
    }
  ],
  "analysisMetadata": {
    "goalsCount": 1,
    "featuresCount": 1,
    "storiesCount": 2,
    "criticalGapsCount": 0,
    "completedAt": "2026-01-10T14:00:00Z"
  }
}
```

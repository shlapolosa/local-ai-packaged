# Architect Output Schema

This document defines the required JSON output schema for the Pre-Feasibility Architect agent.

## Output Requirements

- Output MUST be valid JSON only
- NO markdown, explanations, or conversational text
- Response MUST start with `{` and end with `}`
- All required fields must be present

## JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ArchitectAnalysisOutput",
  "type": "object",
  "required": ["architecture", "tasks", "estimations", "feasibility", "analysisMetadata"],
  "properties": {
    "architecture": {
      "type": "object",
      "description": "Extracted architecture from codebase analysis",
      "properties": {
        "stack": {
          "type": "object",
          "properties": {
            "language": { "type": "string" },
            "framework": { "type": "string" },
            "database": { "type": "string" },
            "orm": { "type": "string" },
            "messaging": { "type": "string" },
            "cache": { "type": "string" }
          }
        },
        "modules": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "type": { "type": "string", "enum": ["domain_module", "infrastructure", "shared"] },
              "path": { "type": "string" },
              "responsibility": { "type": "string" },
              "dependencies": { "type": "array", "items": { "type": "string" } }
            }
          }
        },
        "apis": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "method": { "type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"] },
              "path": { "type": "string" },
              "handler": { "type": "string" },
              "authentication": { "type": "string" }
            }
          }
        },
        "dataModels": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "type": { "type": "string", "enum": ["entity", "dto", "interface"] },
              "location": { "type": "string" },
              "fields": { "type": "array" }
            }
          }
        }
      }
    },
    "tasks": {
      "type": "array",
      "description": "Technical tasks for each story",
      "items": {
        "type": "object",
        "required": ["id", "storyId", "title", "type"],
        "properties": {
          "id": { "type": "string", "pattern": "^T-[0-9]{3}$" },
          "storyId": { "type": "string" },
          "title": { "type": "string" },
          "description": { "type": "string" },
          "type": {
            "type": "string",
            "enum": ["implementation", "modification", "integration", "testing", "documentation", "infrastructure"]
          },
          "impactedModules": { "type": "array", "items": { "type": "string" } },
          "newComponents": { "type": "array", "items": { "type": "string" } },
          "modifiedComponents": { "type": "array", "items": { "type": "string" } },
          "dependencies": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "architectureGaps": {
      "type": "array",
      "description": "Gaps between requirements and current architecture",
      "items": {
        "type": "object",
        "required": ["storyId", "gapType", "description", "severity"],
        "properties": {
          "storyId": { "type": "string" },
          "gapType": {
            "type": "string",
            "enum": ["missing_module", "missing_api", "missing_model", "modification", "integration", "infrastructure", "tech_debt"]
          },
          "description": { "type": "string" },
          "currentState": { "type": "string" },
          "requiredState": { "type": "string" },
          "severity": { "type": "string", "enum": ["critical", "high", "medium", "low"] },
          "suggestedResolution": { "type": "string" }
        }
      }
    },
    "dataflowGaps": {
      "type": "array",
      "description": "Gaps in UI to API to Data flows",
      "items": {
        "type": "object",
        "properties": {
          "storyId": { "type": "string" },
          "uiComponent": { "type": "string" },
          "field": { "type": "string" },
          "issue": { "type": "string", "enum": ["missing_api", "missing_field", "type_mismatch", "missing_model"] },
          "description": { "type": "string" },
          "severity": { "type": "string", "enum": ["critical", "high", "medium", "low"] },
          "resolution": { "type": "string" }
        }
      }
    },
    "missingDefinitions": {
      "type": "object",
      "description": "APIs and models that need to be created",
      "properties": {
        "apis": { "type": "array" },
        "models": { "type": "array" }
      }
    },
    "estimations": {
      "type": "object",
      "description": "Effort estimations using rubric",
      "required": ["tasks", "rollups"],
      "properties": {
        "tasks": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["taskId", "storyId", "rubricScores", "totalScore", "confidence"],
            "properties": {
              "taskId": { "type": "string" },
              "storyId": { "type": "string" },
              "title": { "type": "string" },
              "rubricScores": {
                "type": "object",
                "description": "Scores 0,1,2,3,5,8,13 for each category",
                "properties": {
                  "ui_complexity": { "type": "integer" },
                  "frontend_state": { "type": "integer" },
                  "accessibility": { "type": "integer" },
                  "backend_complexity": { "type": "integer" },
                  "database_changes": { "type": "integer" },
                  "api_complexity": { "type": "integer" },
                  "caching": { "type": "integer" },
                  "fhir_standards": { "type": "integer" },
                  "clinical_workflow": { "type": "integer" },
                  "compliance": { "type": "integer" },
                  "interoperability": { "type": "integer" },
                  "security": { "type": "integer" },
                  "testing_complexity": { "type": "integer" },
                  "documentation": { "type": "integer" },
                  "devops": { "type": "integer" }
                }
              },
              "totalScore": { "type": "integer" },
              "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
              "rationale": { "type": "string" }
            }
          }
        },
        "rollups": {
          "type": "object",
          "properties": {
            "byStory": { "type": "object" },
            "byFeature": { "type": "object" },
            "total": { "type": "integer" },
            "averageConfidence": { "type": "number" }
          }
        }
      }
    },
    "feasibility": {
      "type": "object",
      "description": "Overall feasibility assessment",
      "required": ["score", "summary"],
      "properties": {
        "score": { "type": "string", "enum": ["green", "amber", "red"] },
        "summary": { "type": "string" },
        "criticalBlockers": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "issue": { "type": "string" },
              "impact": { "type": "string" },
              "resolution": { "type": "string" }
            }
          }
        },
        "highRisks": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "risk": { "type": "string" },
              "likelihood": { "type": "string", "enum": ["high", "medium", "low"] },
              "impact": { "type": "string", "enum": ["high", "medium", "low"] },
              "mitigation": { "type": "string" }
            }
          }
        },
        "recommendations": { "type": "array", "items": { "type": "string" } }
      }
    },
    "analysisMetadata": {
      "type": "object",
      "required": ["tasksCreated", "totalEstimatedPoints", "completedAt"],
      "properties": {
        "filesAnalyzed": { "type": "integer" },
        "modulesIdentified": { "type": "integer" },
        "apisFound": { "type": "integer" },
        "modelsFound": { "type": "integer" },
        "tasksCreated": { "type": "integer" },
        "totalEstimatedPoints": { "type": "integer" },
        "completedAt": { "type": "string", "format": "date-time" }
      }
    }
  }
}
```

## Example Output

```json
{
  "architecture": {
    "stack": {
      "language": "TypeScript",
      "framework": "Express.js",
      "database": "SQLite",
      "orm": "Prisma",
      "messaging": null,
      "cache": null
    },
    "modules": [
      {
        "name": "estimates",
        "type": "domain_module",
        "path": "server/src/routes/estimates.js",
        "responsibility": "Estimation CRUD operations",
        "dependencies": ["prisma"]
      }
    ],
    "apis": [
      {
        "method": "GET",
        "path": "/api/v1/estimates",
        "handler": "estimates.list",
        "authentication": "none"
      }
    ],
    "dataModels": [
      {
        "name": "Estimate",
        "type": "entity",
        "location": "server/prisma/schema.prisma",
        "fields": [
          { "name": "id", "type": "string" },
          { "name": "title", "type": "string" }
        ]
      }
    ]
  },
  "tasks": [
    {
      "id": "T-001",
      "storyId": "S-001",
      "title": "Create patient check-in API endpoint",
      "description": "Implement POST /api/v1/checkin endpoint",
      "type": "implementation",
      "impactedModules": ["routes"],
      "newComponents": ["checkin.js"],
      "modifiedComponents": [],
      "dependencies": []
    }
  ],
  "architectureGaps": [
    {
      "storyId": "S-001",
      "gapType": "missing_api",
      "description": "No check-in endpoint exists",
      "currentState": "No patient check-in functionality",
      "requiredState": "POST /api/v1/checkin endpoint",
      "severity": "high",
      "suggestedResolution": "Create new route module for check-in"
    }
  ],
  "dataflowGaps": [],
  "missingDefinitions": {
    "apis": [
      {
        "suggestedPath": "/api/v1/checkin",
        "method": "POST",
        "purpose": "Patient check-in",
        "linkedStory": "S-001"
      }
    ],
    "models": []
  },
  "estimations": {
    "tasks": [
      {
        "taskId": "T-001",
        "storyId": "S-001",
        "title": "Create patient check-in API endpoint",
        "rubricScores": {
          "ui_complexity": 0,
          "frontend_state": 0,
          "accessibility": 0,
          "backend_complexity": 3,
          "database_changes": 2,
          "api_complexity": 2,
          "caching": 0,
          "fhir_standards": 0,
          "clinical_workflow": 1,
          "compliance": 1,
          "interoperability": 0,
          "security": 2,
          "testing_complexity": 2,
          "documentation": 1,
          "devops": 0
        },
        "totalScore": 14,
        "confidence": 0.8,
        "rationale": "Standard REST endpoint with patient data handling"
      }
    ],
    "rollups": {
      "byStory": {
        "S-001": {
          "totalScore": 14,
          "taskCount": 1,
          "averageConfidence": 0.8
        }
      },
      "byFeature": {},
      "total": 14,
      "averageConfidence": 0.8
    }
  },
  "feasibility": {
    "score": "green",
    "summary": "Implementation is straightforward with existing architecture",
    "criticalBlockers": [],
    "highRisks": [],
    "recommendations": [
      "Add authentication before production deployment",
      "Consider caching for frequently accessed patient data"
    ]
  },
  "analysisMetadata": {
    "filesAnalyzed": 15,
    "modulesIdentified": 3,
    "apisFound": 5,
    "modelsFound": 2,
    "tasksCreated": 1,
    "totalEstimatedPoints": 14,
    "completedAt": "2026-01-10T14:00:00Z"
  }
}
```

---
name: coding-workflow
description: "Development cycle task execution workflow. Use when: (1) Executing tasks from Taskmaster backlog, (2) Routing tasks to specialist agents, (3) Managing coding task lifecycle. Integrates with taskmaster-mcp for task operations."
---

# Coding Workflow Skill

This skill enables the Development Cycle to execute tasks from the Taskmaster backlog through specialized coding agents.

## Overview

The coding workflow:
1. Reads tasks from `.taskmaster/tasks/tasks.json`
2. Routes tasks to domain-specific specialist agents
3. Manages task status through execution lifecycle
4. Handles failures and human escalation

## Development Cycle Position

```
ADM Cycle (Architecture)
    │
    ▼ (OAM Deployed, Infrastructure Ready)
Development Cycle (Execution)
    ├── TechLead: PRD → Tasks
    ├── Coding Orchestrator: Route tasks
    └── Specialists: Execute tasks
```

## Agents

### Orchestrator

| Agent | Role |
|-------|------|
| `coding-orchestrator` | Central coordinator, task routing, status management |

### Specialists

| Agent | Domain | Expertise |
|-------|--------|-----------|
| `frontend-coder` | UI/Components | React, Vue, CSS, Tailwind |
| `backend-coder` | APIs/Logic | Node, Python, Go, databases |
| `infra-coder` | Infrastructure | Kubernetes, Terraform, OAM |
| `devops-coder` | CI/CD | Pipelines, Docker, GitHub Actions |
| `data-coder` | Data | Schemas, migrations, ORMs |
| `testing-agent` | Quality | Unit tests, E2E, coverage |

## Task Routing

### Domain Classification

Tasks are classified by analyzing title, description, and details:

| Domain | Keywords |
|--------|----------|
| frontend | component, ui, react, css, tailwind, page, layout |
| backend | api, endpoint, service, controller, middleware |
| infrastructure | kubernetes, terraform, helm, oam, cluster |
| devops | ci/cd, pipeline, docker, github actions, deploy |
| data | database, schema, migration, sql, model |
| testing | test, spec, unit test, e2e, coverage |

### Routing Algorithm

```
1. Extract text from task.title + task.description + task.details
2. Count keyword matches per domain
3. Select domain with highest score
4. If score < 3, use LLM classification fallback
5. Route to {domain}-coder agent
```

## Workflow Loop

```
START
    │
    ▼
[Get next_task] ──► null? ──► END (All Done)
    │
    ▼
[set_task_status("in-progress")]
    │
    ▼
[Classify domain]
    │
    ▼
[Route to specialist agent]
    │
    ▼
[Specialist executes]
    │
    ├── Success ──► [set_task_status("done")] ──► [Commit changes]
    │
    ├── Recoverable ──► [Retry once]
    │
    └── Blocking ──► [set_task_status("review")] ──► [Log for human]
    │
    ▼
[LOOP back to next_task]
```

## Task Context

When routing to specialists, provide:

```json
{
    "task_id": "5",
    "title": "Implement user dashboard",
    "description": "Create main dashboard view",
    "details": "Step-by-step implementation...",
    "testStrategy": "Unit tests for components",
    "priority": "high",
    "workspace_path": "/workspace/my-service"
}
```

## Error Handling

### Failure Categories

| Type | Action |
|------|--------|
| Transient | Auto-retry once (timeout, rate limit) |
| Recoverable | Retry with error context (test failure) |
| Blocking | Mark "review", continue (missing deps) |
| Critical | Halt + notify (security issue) |

### Review Queue

Blocked tasks are marked "review" for human intervention:

```json
{
    "task_id": "7",
    "status": "review",
    "reason": "Missing API credentials",
    "error_details": "...",
    "recommendation": "Add STRIPE_API_KEY to .env"
}
```

## Integration with Taskmaster MCP

This skill depends on `taskmaster-mcp` for all task operations:

| Operation | Taskmaster Tool |
|-----------|-----------------|
| Get next task | `next_task` |
| Update status | `set_task_status` |
| List all tasks | `get_tasks` |
| Get task details | `get_task` |
| Add discovered work | `add_task` |

## Specialist Agent Guidelines

Each specialist should:

1. **Read the task** - Understand title, description, details, testStrategy
2. **Analyze codebase** - Read existing files, understand patterns
3. **Implement changes** - Write code following project conventions
4. **Run tests** - Execute tests per testStrategy
5. **Report result** - Return success/failure with details

### Specialist Output Format

```json
{
    "status": "success|failure",
    "files_modified": ["src/components/Dashboard.tsx"],
    "tests_run": 12,
    "tests_passed": 12,
    "coverage": "85%",
    "notes": "Added responsive breakpoints"
}
```

## Best Practices

### For Orchestrator
1. Always use `next_task` to respect dependencies
2. Mark tasks "in-progress" before delegating
3. Log progress after each task
4. Don't skip review queue for unclear tasks

### For Specialists
1. Read existing code before modifying
2. Follow project coding conventions
3. Write tests per testStrategy
4. Commit after successful implementation
5. Report detailed errors on failure

## Output Format

### Progress Report

```json
{
    "cycle_status": "running",
    "tasks": {
        "completed": 15,
        "in_progress": 1,
        "pending": 7,
        "review": 2
    },
    "current_task": {
        "id": "16",
        "title": "Add pagination",
        "agent": "frontend-coder"
    }
}
```

### Completion Report

```json
{
    "cycle_status": "complete",
    "summary": {
        "total": 25,
        "completed": 23,
        "review_needed": 2
    },
    "commits": ["abc123", "def456", "..."],
    "review_items": [
        {"task_id": "7", "reason": "Missing credentials"}
    ]
}
```

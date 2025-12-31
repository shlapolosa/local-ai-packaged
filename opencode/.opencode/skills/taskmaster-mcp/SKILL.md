---
name: taskmaster-mcp
description: "Task management using Taskmaster MCP. Use when: (1) Breaking down PRDs into development tasks, (2) Analyzing task complexity, (3) Expanding large tasks into subtasks, (4) Managing task status during development. Integrates with Claude Task Master MCP server using local Ollama for AI operations."
---

# Taskmaster MCP Skill

This skill enables AI agents to manage development tasks using the Taskmaster MCP server with local Ollama.

## Overview

Taskmaster is an AI-powered task management system that:
1. Parses PRDs into structured tasks
2. Analyzes task complexity (1-10 scale)
3. Expands complex tasks into manageable subtasks
4. Tracks task status through development lifecycle

## MCP Server Configuration

The Taskmaster MCP server runs via npx and connects to local Ollama:

```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "OLLAMA_BASE_URL": "http://ollama:11434/api",
        "TASK_MASTER_TOOLS": "standard"
      }
    }
  }
}
```

**Note**: No API keys required for local Ollama.

## Project Structure

Taskmaster creates this structure in each service repo:

```
.taskmaster/
├── config.json           # Model and project config
├── docs/
│   └── prd.txt          # PRD copied here for parsing
└── tasks/
    └── tasks.json       # Generated task hierarchy
```

## Complexity Scale

| Level | Size | Description | Action |
|-------|------|-------------|--------|
| 1-3 | Small | Single function/component | Keep |
| 4-6 | Medium | Feature with 2-3 parts | Keep |
| 7-8 | Large | Multi-component feature | Expand |
| 9-10 | Epic | Full module/system | Expand |

**Target**: All tasks should be complexity ≤ 6 (medium or smaller)

## Available Tools

### Project Setup
| Tool | Purpose |
|------|---------|
| `initialize_project` | Create .taskmaster directory structure |

### PRD Processing
| Tool | Purpose |
|------|---------|
| `parse_prd` | Convert PRD to tasks.json |

### Task Management
| Tool | Purpose |
|------|---------|
| `get_tasks` | List all tasks with status |
| `get_task` | Get single task details |
| `next_task` | Get next pending task |
| `set_task_status` | Update task status (pending/in-progress/done) |
| `add_task` | Add new task manually |
| `remove_task` | Remove a task |
| `update_subtask` | Update subtask details |

### Task Expansion
| Tool | Purpose |
|------|---------|
| `expand_task` | Break single task into subtasks |
| `expand_all` | Expand all pending tasks |
| `add_subtask` | Add subtask to existing task |

### Analysis
| Tool | Purpose |
|------|---------|
| `analyze_project_complexity` | Analyze complexity scores |
| `complexity_report` | Generate detailed report |

### Generation
| Tool | Purpose |
|------|---------|
| `generate` | Generate task from description |

## Workflow

### TechLead Agent Workflow
```
1. initialize_project (if needed)
2. Copy PRD to .taskmaster/docs/prd.txt
3. parse_prd → creates tasks.json
4. analyze_project_complexity → identify large tasks
5. Loop: expand_task for each task > complexity 6
6. Re-analyze until all tasks ≤ 6
7. get_tasks → output final list
```

### Coding Agent Workflow
```
1. next_task → get highest priority pending task
2. set_task_status(id, "in-progress")
3. Implement the task
4. set_task_status(id, "done")
5. Repeat until no pending tasks
```

## PRD Format Requirements

PRDs must follow the 7-section Taskmaster format for optimal parsing:

1. **Overview** - Problem, audience, value proposition
2. **Core Features** - What it does, why, how
3. **User Experience** - Personas, flows, design
4. **Technical Architecture** - Components, data, APIs
5. **Development Roadmap** - Phased scope
6. **Logical Dependency Chain** - Task sequencing
7. **Appendix** - References, specs

See `references/prd-format.md` for the complete template.

## Ollama Configuration

Each service repo needs `.taskmaster/config.json`:

```json
{
  "global": {
    "ollamaBaseURL": "http://ollama:11434/api"
  },
  "models": {
    "main": {
      "provider": "ollama",
      "modelId": "qwen2.5:7b-instruct-q4_K_M"
    },
    "research": {
      "provider": "ollama",
      "modelId": "qwen2.5:7b-instruct-q4_K_M"
    },
    "fallback": {
      "provider": "ollama",
      "modelId": "qwen2.5:7b-instruct-q4_K_M"
    }
  }
}
```

Copy from `templates/config.json` when initializing new projects.

## Task JSON Schema

```json
{
  "tasks": [
    {
      "id": "1",
      "title": "Implement User Authentication",
      "description": "Set up JWT-based authentication system",
      "status": "pending",
      "priority": "high",
      "complexity": 5,
      "dependencies": [],
      "subtasks": [
        {
          "id": "1.1",
          "title": "Create auth middleware",
          "status": "pending",
          "complexity": 3
        }
      ]
    }
  ]
}
```

## Best Practices

### For TechLead
1. Always analyze complexity after parsing
2. Expand iteratively (one pass at a time)
3. Set max depth of 3 for subtask hierarchy
4. Document expansion rationale

### For Coding Agent
1. Always claim task with `set_task_status` before starting
2. Complete subtasks before parent task
3. Respect dependency order
4. Update status promptly

## Integration

### Input Sources
- PRD from BA agent (`docs/PRD.md`)

### Output Destinations
- Task backlog (`.taskmaster/tasks/tasks.json`)
- GitHub commit for persistence

### Status Broadcasting
- Redis pub/sub for real-time updates
- Slack notifications for milestones

## References

- `references/taskmaster-commands.md` - Complete MCP tool documentation
- `references/prd-format.md` - PRD format specification
- `templates/config.json` - Ollama configuration template

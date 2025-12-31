# Taskmaster MCP Commands Reference

Complete reference for all Taskmaster MCP tools available in Standard mode.

## Project Initialization

### initialize_project
Initialize Taskmaster in a new project.

```
Tool: initialize_project
Parameters:
  - project_root: string (optional) - Path to project root, defaults to cwd
  - name: string (optional) - Project name
```

**Creates:**
```
.taskmaster/
├── config.json
├── docs/
└── tasks/
```

## PRD Processing

### parse_prd
Parse a Product Requirements Document into tasks.

```
Tool: parse_prd
Parameters:
  - prd_path: string (required) - Path to PRD file (usually .taskmaster/docs/prd.txt)
  - output_path: string (optional) - Custom output path for tasks.json
```

**Returns:**
```json
{
  "success": true,
  "tasks_created": 15,
  "output_path": ".taskmaster/tasks/tasks.json"
}
```

## Task Retrieval

### get_tasks
Get all tasks with optional filtering.

```
Tool: get_tasks
Parameters:
  - status: string (optional) - Filter by status: "pending" | "in-progress" | "done" | "review" | "deferred" | "cancelled"
  - include_subtasks: boolean (optional) - Include subtasks in output, default true
```

**Returns:**
```json
{
  "tasks": [
    {
      "id": "1",
      "title": "Task title",
      "status": "pending",
      "complexity": 5,
      "subtasks": [...]
    }
  ],
  "total": 15,
  "by_status": {
    "pending": 10,
    "in-progress": 2,
    "done": 3
  }
}
```

### get_task
Get a single task by ID.

```
Tool: get_task
Parameters:
  - task_id: string (required) - Task ID (e.g., "1" or "1.2" for subtask)
```

**Returns:**
```json
{
  "id": "1",
  "title": "Implement User Authentication",
  "description": "Full description...",
  "status": "pending",
  "priority": "high",
  "complexity": 5,
  "dependencies": ["2", "3"],
  "test_strategy": "Unit tests for auth functions",
  "subtasks": [...]
}
```

### next_task
Get the next task to work on (highest priority pending task with met dependencies).

```
Tool: next_task
Parameters: none
```

**Returns:**
```json
{
  "id": "5",
  "title": "Create API endpoints",
  "description": "...",
  "status": "pending",
  "priority": "high",
  "complexity": 4,
  "dependencies_met": true
}
```

## Task Status Management

### set_task_status
Update task status.

```
Tool: set_task_status
Parameters:
  - task_id: string (required) - Task ID
  - status: string (required) - New status: "pending" | "in-progress" | "done" | "review" | "deferred" | "cancelled"
```

**Status Values:**
- `pending` - Not started
- `in-progress` - Currently being worked on
- `done` - Completed
- `review` - Awaiting review
- `deferred` - Postponed
- `cancelled` - Not needed

## Task Creation

### add_task
Add a new task manually.

```
Tool: add_task
Parameters:
  - title: string (required) - Task title
  - description: string (optional) - Task description
  - priority: string (optional) - "high" | "medium" | "low"
  - dependencies: array<string> (optional) - Task IDs this depends on
```

### add_subtask
Add a subtask to an existing task.

```
Tool: add_subtask
Parameters:
  - parent_id: string (required) - Parent task ID
  - title: string (required) - Subtask title
  - description: string (optional) - Subtask description
```

### remove_task
Remove a task.

```
Tool: remove_task
Parameters:
  - task_id: string (required) - Task ID to remove
```

### update_subtask
Update subtask details.

```
Tool: update_subtask
Parameters:
  - subtask_id: string (required) - Subtask ID (e.g., "1.2")
  - title: string (optional) - New title
  - description: string (optional) - New description
  - status: string (optional) - New status
```

## Task Expansion

### expand_task
Break a task into subtasks using AI.

```
Tool: expand_task
Parameters:
  - task_id: string (required) - Task ID to expand
  - num_subtasks: number (optional) - Target number of subtasks (default: auto)
  - force: boolean (optional) - Expand even if already has subtasks
```

**Returns:**
```json
{
  "success": true,
  "task_id": "3",
  "subtasks_created": 4,
  "subtasks": [
    { "id": "3.1", "title": "...", "complexity": 4 },
    { "id": "3.2", "title": "...", "complexity": 5 },
    { "id": "3.3", "title": "...", "complexity": 3 },
    { "id": "3.4", "title": "...", "complexity": 4 }
  ]
}
```

### expand_all
Expand all pending tasks that meet criteria.

```
Tool: expand_all
Parameters:
  - min_complexity: number (optional) - Only expand tasks with complexity >= this value (default: 7)
  - force: boolean (optional) - Expand even if already has subtasks
```

## Complexity Analysis

### analyze_project_complexity
Analyze complexity of all tasks.

```
Tool: analyze_project_complexity
Parameters: none
```

**Returns:**
```json
{
  "total_tasks": 15,
  "by_complexity": {
    "small": { "count": 5, "range": "1-3" },
    "medium": { "count": 6, "range": "4-6" },
    "large": { "count": 3, "range": "7-8" },
    "epic": { "count": 1, "range": "9-10" }
  },
  "tasks_needing_expansion": ["3", "7", "10", "12"],
  "average_complexity": 5.2
}
```

### complexity_report
Generate detailed complexity report.

```
Tool: complexity_report
Parameters:
  - output_format: string (optional) - "json" | "markdown" | "text"
```

## Task Generation

### generate
Generate a task from natural language description.

```
Tool: generate
Parameters:
  - description: string (required) - Natural language task description
  - parent_id: string (optional) - Add as subtask to this parent
```

**Example:**
```
Tool: generate
Parameters:
  description: "Add password reset functionality with email verification"
```

**Returns:**
```json
{
  "id": "16",
  "title": "Implement Password Reset Flow",
  "description": "Add password reset functionality with email verification link",
  "priority": "medium",
  "complexity": 5,
  "test_strategy": "E2E test for complete reset flow"
}
```

## Error Handling

All tools return errors in this format:
```json
{
  "success": false,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with ID '99' does not exist"
  }
}
```

**Common Error Codes:**
- `TASK_NOT_FOUND` - Task ID doesn't exist
- `INVALID_STATUS` - Invalid status value
- `DEPENDENCY_CYCLE` - Circular dependency detected
- `PRD_PARSE_ERROR` - Failed to parse PRD
- `EXPANSION_FAILED` - AI expansion failed

## Best Practices

1. **Always check complexity after parsing** - Some tasks may be too large
2. **Expand iteratively** - Don't expand all at once; check results
3. **Respect dependencies** - Use `next_task` to get properly ordered work
4. **Update status promptly** - Helps coordination in multi-agent scenarios
5. **Use generate for ad-hoc tasks** - When discoveries need tracking

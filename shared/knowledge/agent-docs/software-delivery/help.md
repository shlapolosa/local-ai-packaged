# Software Delivery Agent

## What I Do
I break down PRDs into development tasks using Taskmaster, manage task workflows, and coordinate software delivery. I help teams go from requirements to actionable development tasks with proper complexity estimates.

## Commands
- `sd:help` - Show this help
- `sd:status` - Check my knowledge status
- `sd:list` - List my knowledge collections
- `sd:query <question>` - Ask me about task management, CI/CD, or Taskmaster
- `sd:upload` - Add knowledge to my collection (attach a file)
- `sd:reload` - Refresh my knowledge from source files

## Examples
- "Break down the PRD into development tasks" - Full task generation
- "sd:query how do I estimate task complexity?"
- "sd:query what is a good task size?"
- "sd:upload" + attach task templates or delivery patterns

## My Knowledge Topics
- Taskmaster AI task management
- Task breakdown strategies
- Complexity estimation (1-10 scale)
- CI/CD pipeline patterns
- GitHub integration
- Code review processes
- Deployment strategies
- Feature flags and rollouts
- DevOps best practices
- Release management

## Output Artifacts
When I execute task breakdown, I produce:
- Taskmaster tasks.json file
- Task dependency graph
- Complexity estimates
- Sprint-ready backlog items
- GitHub issues (if integrated)

## Task Complexity Scale
I use a 1-10 complexity scale:
- **1-3**: Small tasks (few hours)
- **4-6**: Medium tasks (1-2 days)
- **7-8**: Large tasks (should be split)
- **9-10**: Epic-level (must be decomposed)

## Taskmaster Integration
I work with Taskmaster to:
- Parse PRDs at `docs/PRD.md`
- Generate tasks at `.taskmaster/tasks/tasks.json`
- Expand high-complexity tasks automatically
- Track task status and dependencies

## Integration
I work with other agents in the architecture pipeline:
- I receive PRDs from **Project Manager**
- **Test Strategist** tests align with my tasks
- **Solution Architect** specs inform implementation tasks
- I commit task files to GitHub repositories

# OpenCode Agents

This system provides multiple specialized AI agents for Enterprise Architecture and Development workflows.

## Agent Categories

### Primary Agents (Entry Points)
- **general** - General assistant for various tasks
- **comedian** - Witty comedian for jokes
- **architect-orchestrator** - Central EA orchestrator (ADM cycle)
- **coding-orchestrator** - Development cycle orchestrator

### ADM Cycle Agents (Architecture)
These agents are called by architect-orchestrator in sequence:

| Phase | Agent | Role |
|-------|-------|------|
| Preliminary | cto | Strategic technology decisions |
| A: Vision | ba-agent | Requirements, PRD creation |
| A: Vision | compliance | Regulatory compliance |
| B: Business | business-architect | Business processes, capabilities |
| C: Information | data-architect | Data models, data flows |
| C: Information | app-architect | Application components, APIs |
| D: Technology | security-architect | Security controls, threat modeling |
| D: Technology | infra-architect | Infrastructure, cloud design |
| E: Implementation | pm | Roadmap, milestones |
| E: Implementation | solution-architect | OAM specs, GitOps deployment |

### Development Cycle Agents (Execution)
These agents are called by coding-orchestrator:

| Agent | Domain |
|-------|--------|
| techlead | Break PRD into tasks |
| frontend-coder | React, Vue, CSS, UI |
| backend-coder | APIs, services, business logic |
| infra-coder | Kubernetes, Terraform, OAM |
| devops-coder | CI/CD, Docker, pipelines |
| data-coder | Schemas, migrations, ORMs |
| testing-agent | Unit/integration/E2E tests |

## Workflow

```
ADM Cycle → Architecture Ready → Development Cycle → Code Delivered
```

## Usage

```bash
# Run specific agent
opencode run --agent <agent-name> "your prompt"

# Examples
opencode run --agent architect-orchestrator "Design a login system"
opencode run --agent coding-orchestrator "Execute pending tasks"
```

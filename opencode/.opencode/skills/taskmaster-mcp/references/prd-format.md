# Taskmaster PRD Format Specification

This document defines the 7-section PRD format required for optimal Taskmaster parsing.

## Overview

Taskmaster's `parse_prd` tool works best with structured PRDs that follow this format. The more detailed and well-organized the PRD, the better the generated tasks will be.

## Required Sections

### 1. Overview
High-level context about the product.

```markdown
## 1. Overview

### Problem Statement
{What problem does this solve? Be specific about pain points.}

### Target Audience
{Who is this for? Include primary and secondary users.}

### Value Proposition
{Why would users choose this? What's the unique value?}
```

### 2. Core Features
Feature descriptions with implementation context.

```markdown
## 2. Core Features

### Feature 1: {Name}
- **What it does**: {Clear functional description}
- **Why it's important**: {Business value / user benefit}
- **How it works**: {High-level technical approach}

### Feature 2: {Name}
- **What it does**: {Description}
- **Why it's important**: {Value}
- **How it works**: {Approach}

{Continue for all major features...}
```

### 3. User Experience
User-centered design considerations.

```markdown
## 3. User Experience

### User Personas
- **Persona 1: {Name/Role}**
  - Goals: {What they want to achieve}
  - Frustrations: {Current pain points}
  - Context: {When/where they use the product}

- **Persona 2: {Name/Role}**
  - Goals: {Goals}
  - Frustrations: {Pain points}
  - Context: {Usage context}

### User Flows
1. **{Primary Flow Name}**
   - Step 1: {Action}
   - Step 2: {Action}
   - Step 3: {Action}
   - Outcome: {Expected result}

2. **{Secondary Flow Name}**
   - Step 1: {Action}
   - Step 2: {Action}
   - Outcome: {Expected result}

### Design Considerations
- {Key UX principle 1 - e.g., "Mobile-first responsive design"}
- {Key UX principle 2 - e.g., "Accessibility compliance (WCAG 2.1 AA)"}
- {Key UX principle 3}
```

### 4. Technical Architecture
System design and implementation details.

```markdown
## 4. Technical Architecture

### System Components
- **{Component 1}**: {Purpose and responsibilities}
- **{Component 2}**: {Purpose and responsibilities}
- **{Component 3}**: {Purpose and responsibilities}

### Data Structures
- **{Entity 1}**: {Key fields and relationships}
- **{Entity 2}**: {Key fields and relationships}

### APIs
- **{Endpoint 1}**: {Method} - {Purpose}
- **{Endpoint 2}**: {Method} - {Purpose}
- **{Endpoint 3}**: {Method} - {Purpose}

### Infrastructure
- {Hosting/deployment requirement}
- {Database requirement}
- {Caching/performance requirement}
- {Security requirement}
```

### 5. Development Roadmap
Phased delivery without time estimates.

```markdown
## 5. Development Roadmap

### Phase 1: MVP
**Scope:**
- {Core feature 1}
- {Core feature 2}
- {Essential infrastructure}

**Success Criteria:**
- {Measurable outcome 1}
- {Measurable outcome 2}

### Phase 2: Enhancement
**Scope:**
- {Secondary feature 1}
- {Secondary feature 2}
- {Integration improvements}

**Success Criteria:**
- {Measurable outcome 1}
- {Measurable outcome 2}

### Phase 3: Scale
**Scope:**
- {Advanced feature 1}
- {Advanced feature 2}
- {Performance optimization}

**Success Criteria:**
- {Measurable outcome 1}
- {Measurable outcome 2}
```

### 6. Logical Dependency Chain
Task sequencing for Taskmaster to understand dependencies.

```markdown
## 6. Logical Dependency Chain

### Foundation Layer (Build First)
1. **{Task/Feature}** - Required by: {list downstream dependents}
2. **{Task/Feature}** - Required by: {list downstream dependents}
3. **{Task/Feature}** - Required by: {list downstream dependents}

### Core Layer (Build Second)
4. **{Task/Feature}** - Depends on: {list upstream dependencies}
5. **{Task/Feature}** - Depends on: {list upstream dependencies}
6. **{Task/Feature}** - Depends on: {list upstream dependencies}

### Integration Layer (Build Third)
7. **{Task/Feature}** - Depends on: {list upstream dependencies}
8. **{Task/Feature}** - Depends on: {list upstream dependencies}

### Polish Layer (Build Last)
9. **{Task/Feature}** - Depends on: {list upstream dependencies}
10. **{Task/Feature}** - Depends on: {list upstream dependencies}
```

### 7. Appendix
Supporting materials.

```markdown
## 7. Appendix

### Research References
- {Reference 1: Link or citation}
- {Reference 2: Link or citation}

### Technical Specifications
- {Spec 1: Details}
- {Spec 2: Details}

### Glossary
- **{Term 1}**: {Definition}
- **{Term 2}**: {Definition}
```

## Complete Example

For a complete PRD example, reference the industry-specific example file from the configuration:

```python
import json
config_path = "/root/.config/opencode/industry-config.json"
with open(config_path) as f:
    config = json.load(f)

# Get PRD example path from BA agent config
ba_config = config.get("agentKnowledge", {}).get("ba-agent", {})
prd_example_path = ba_config.get("prdExample")
# Or from knowledgeBase
prd_example_path = config.get("knowledgeBase", {}).get("prdExample")

# Load /root/.config/opencode/{prd_example_path} for complete example
```

The example file (e.g., `.opencode/examples/healthcare-prd-example.md`) contains a complete PRD following the 7-section format with industry-specific:
- Problem statements and value propositions
- User personas and flows
- Technical architecture patterns
- Compliance considerations
- Domain-specific terminology

## Best Practices

### For BA Agents
1. **Be specific** - Vague requirements produce vague tasks
2. **Include the "why"** - Helps Taskmaster prioritize
3. **Define dependencies** - Section 6 is critical for ordering
4. **Scope each phase** - Clear boundaries help task generation
5. **Use consistent naming** - Same terms throughout document

### Common Mistakes
- Missing dependency chain (Section 6)
- Vague feature descriptions
- No technical architecture details
- Mixing implementation with requirements
- Omitting success criteria

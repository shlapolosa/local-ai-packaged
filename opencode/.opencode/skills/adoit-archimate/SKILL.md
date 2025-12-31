---
name: adoit-archimate
description: "Enterprise Architecture management with ADOIT using ArchiMate 3.1. Use when: (1) Analyzing current state architecture in ADOIT repositories, (2) Creating or updating ArchiMate models via Excel import, (3) Working with capability maps, application portfolios, or technology landscapes, (4) Designing future state architectures for healthcare or enterprise platforms, (5) Generating ADOIT-compliant import files for any ArchiMate element type. Supports all 61 ArchiMate element types and 11 relationship types."
---

# ADOIT ArchiMate Skill

This skill enables enterprise architects to interact with ADOIT repositories for ArchiMate-based architecture management.

## Overview

ADOIT is BOC Group's Enterprise Architecture tool supporting ArchiMate 3.1 and TOGAF 9. This skill provides:

1. **Current State Analysis** - Query and analyze existing architecture via API
2. **Future State Design** - Generate ADOIT-compliant Excel imports for new/updated elements
3. **Capability Management** - Work with healthcare and enterprise capability models
4. **Architecture Validation** - Ensure ArchiMate compliance and relationship correctness

## ADOIT Integration Approaches

### Configuration

Create a `.env` file with your ADOIT credentials:

```bash
# Copy the template
cp assets/.env.example .env

# Edit with your credentials
ADOIT_URL=https://adoit-ce.boc-cloud.com
ADOIT_USERNAME=your.email@example.com
ADOIT_PASSWORD=your_password
ADOIT_REPOSITORY_ID=optional_repo_id
```

**Security Note**: Never commit `.env` files with real credentials to version control.

### API Access (Read Operations)
ADOIT Enterprise Edition provides REST API for reading:
- Repository objects and relationships
- Model views and diagrams
- Object attributes and metadata

**Note**: ADOIT Community Edition restricts API write operations (POST/PATCH/DELETE return HTTP 403).

### Excel Import (Create/Update Operations)
All ADOIT editions support Excel import for bulk data operations:
- Use `scripts/adoit_excel_generator.py` to generate compliant files
- Template structure must match ADOIT's expected format exactly
- Relationship columns use `(->Target)` and `(<-Source)` notation

## Architecture Workflow

### Step 1: Understand Current State
```bash
# Using .env file (recommended)
python scripts/adoit_client.py list-repos
python scripts/adoit_client.py find Capability
python scripts/adoit_client.py get "element-id"

# Or with explicit credentials
python scripts/adoit_client.py --url https://... --username user --password pass list-repos
```

```python
# In Python code
from scripts.adoit_client import ADOITClient

# Load from .env file
client = ADOITClient.from_env()

# Or explicit
client = ADOITClient(
    base_url="https://adoit-ce.boc-cloud.com",
    username="user@example.com",
    password="password"
)

capabilities = client.find_elements("Capability")
```

### Step 2: Design Changes
1. Identify gaps between current and target state
2. Map new elements to ArchiMate types
3. Define relationships (composition, realization, serving, etc.)

### Step 3: Generate Import File
```python
from scripts.adoit_excel_generator import ADOITExcelGenerator

gen = ADOITExcelGenerator(template_path="assets/templates/ADOIT_Template_EN.xlsx")

# Add elements with relationships
gen.add_capability("New Capability", 
    description="Description here",
    composition_capability=["Child1", "Child2"])  # Parent->Children

gen.save("output.xlsx")
```

### Step 4: Import to ADOIT
1. Navigate to Administration → Import/Export → Excel Import
2. Select generated file
3. Review import preview
4. Confirm import

## ArchiMate Element Types

### Business Layer
- Business Actor, Business Role, Business Collaboration
- Business Process, Business Function, Business Interaction, Business Event, Business Service
- Business Object, Contract, Representation
- Product

### Application Layer
- Application Component, Application Collaboration
- Application Function, Application Process, Application Interaction, Application Event, Application Service
- Application Interface
- Data Object

### Technology Layer
- Node, Device, System Software
- Technology Collaboration, Technology Function, Technology Process, Technology Interaction, Technology Event, Technology Service
- Technology Interface
- Path, Communication Network, Distribution Network
- Artifact

### Strategy Layer
- Resource, Capability, Value Stream, Course of Action

### Motivation Layer
- Stakeholder, Driver, Assessment
- Goal, Outcome, Principle, Requirement, Constraint
- Meaning, Value

### Implementation Layer
- Work Package, Deliverable, Implementation Event, Plateau, Gap

### Other
- Location, Grouping, Junction

## Relationship Types

| Relationship | Notation | Description |
|-------------|----------|-------------|
| Composition | `(->Target)` | Parent contains children (strong ownership) |
| Aggregation | `(->Target)` | Parent groups children (weak ownership) |
| Assignment | `(->Target)` | Resource assigned to behavior |
| Realization | `(->Target)` | Concrete realizes abstract |
| Serving | `(->Target)` | Provider serves consumer |
| Access | `(->Target)` | Behavior accesses data |
| Influence | `(->Target)` | Element influences another |
| Triggering | `(->Target)` | Behavior triggers another |
| Flow | `(->Target)` | Transfer between behaviors |
| Specialization | `(->Target)` | Specific extends generic |
| Association | `(->Target)` | General relationship |

### Relationship Direction in Excel
- `Composition (->Capability)` - This element composes (contains) the targets
- `Composition (<-Capability)` - This element is composed BY (child of) the targets

**Important**: For hierarchies (parent-child), use reverse notation where each CHILD specifies its PARENT:
```
Child Name | Composition (<-Capability) = Parent Name
```

## Healthcare Capability Model

See `references/healthcare-capability-model.md` for the complete Healthcare Provider Reference Model with 1,666 capabilities across 4 levels.

### Capability Hierarchy
- **L1**: 42 top-level domains (e.g., Patient Access, Clinical Operations)
- **L2**: 353 functional areas
- **L3**: 1,042 specific capabilities
- **L4**: 229 detailed sub-capabilities

## Architecture Role Guidelines

### Business Architect
- Focus on L1-L2 capabilities and business processes
- Reference `references/healthcare-capability-model.md` for domain mapping
- Use Goal, Driver, Stakeholder elements for motivation architecture

### Application Architect
- Focus on L3-L4 capabilities for solution design
- Map Application Components to capabilities via Realization relationships
- Define Application Services and Interfaces

### Infrastructure Architect
- Focus on Node, Device, System Software elements
- Map technology to applications via Assignment/Realization
- Define Communication Networks and Paths

### Data Architect
- Focus on Data Object and Business Object elements
- Define Access relationships from processes/functions
- Map data to applications and storage

## Best Practices

### Naming Conventions
- Use business-meaningful names (not technical identifiers)
- Be consistent with existing repository naming
- Avoid special characters that may cause import issues

### Relationship Guidelines
- Every Application Component should realize at least one Capability
- Use Composition for true part-of relationships
- Use Aggregation for logical groupings
- Avoid circular dependencies

### Import Strategy
- Import in dependency order (parents before children)
- For large imports, consider batching by domain
- Always backup repository before bulk imports

## Scripts Reference

- `scripts/adoit_excel_generator.py` - Generate ADOIT-compliant Excel files
- `scripts/adoit_client.py` - API client for querying ADOIT (Enterprise Edition)
- `scripts/validate_import.py` - Validate Excel file before import

## Templates

- `assets/templates/ADOIT_Template_EN.xlsx` - English import template
- `assets/capability-models/healthcare_provider_v2.xlsx` - Healthcare capability model

## GitHub Artifact Persistence

All generated architecture artifacts (Excel imports, capability models) MUST be committed to GitHub for version control and collaboration.

### Artifact Commit Workflow

After generating any ADOIT import file:

```bash
# Navigate to architecture workspace
cd /workspace/architecture

# Stage the generated artifact
git add initiatives/{initiative-name}/adoit-import.xlsx
git add initiatives/{initiative-name}/design/*.xlsx
git add initiatives/{initiative-name}/requirements/*.xlsx

# Commit with descriptive message
git commit -m "feat({initiative}): Add ADOIT ArchiMate import

- Generated: {list of files}
- Elements: {count} capabilities, {count} components
- Phase: ADM Phase {phase}

🤖 Generated by {agent-name} agent"

# Push to remote
git push origin main
```

### Commit Message Format

```
feat({initiative}): {brief description}

- Type: ADOIT Excel Import
- ArchiMate Elements: {element types added}
- Relationships: {relationship types}
- Phase: ADM Phase {A-H}

🤖 Generated by {agent-name} agent
```

### When to Commit

Commit artifacts at these checkpoints:
1. **After SA design phase** - Application components, data objects
2. **After BA requirements** - Business processes, actors, goals
3. **After EA governance review** - Capabilities, standards alignment
4. **Before PM PRD consolidation** - Ensures all artifacts are versioned

### Branch Strategy

- `main` - Production-ready architecture artifacts
- `initiative/{name}` - Work-in-progress for specific initiatives
- Always create PR for main branch merges

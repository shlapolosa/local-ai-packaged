# Pipeline Evaluation Questions

## Intent Summary

The pipeline should:
- Be **predictable** - consistent output for given input
- Be **deterministic** - traceability from BRD all the way to PRD
- Produce PRD following **RPG template** format (`.taskmaster/templates/example_prd_rpg.txt`)
- Output **strict ArchiMate conformance** - visualizable in Archi and other tools
- Enable **traceability** from every story to business outcomes (tacitly)

**Evaluation Flow:**
```
Requirements → Problem Domain derivation
Goals + Outcomes → Capabilities + Processes → Applications + Tech → Story
```

---

## Questions to Address After Testing

### 1. RPG PRD Template Conformance

- Should the Architecture Pipeline generate the PRD directly in RPG format, or should it generate structured data that gets transformed into RPG format?
- Does the current `prd_md` artifact already follow RPG structure, or does it need modification?

### 2. Traceability Encoding

The flow: `Goals + Outcomes → Capabilities + Processes → Applications + Tech → Story`

- How should traceability be encoded across artifacts?
  - **Option A**: Explicit IDs (e.g., `GOAL-001` → `CAP-001` → `APP-001` → `STORY-001`)
  - **Option B**: Naming conventions with embedded references
  - **Option C**: Metadata fields (JSON) that link artifacts
- Should the ArchiMate XML include relationship elements (`<relationship>`) that explicitly connect layers?

### 3. ArchiMate Strict Conformance

- Which ArchiMate version? (3.1 / 3.2?)
- Should we include the ArchiMate exchange format header with proper namespaces for Archi import?
- Should we enforce specific viewpoint constraints (e.g., Business Layer viewpoint, Application Cooperation viewpoint)?
- Which tool(s) should we validate against? (Archi, others?)

### 4. Determinism vs LLM Variability

- What level of consistency is acceptable?
  - **Structural consistency**: Same sections, same schema, same relationships
  - **Content consistency**: Similar wording/descriptions for same input
- Should we use temperature=0 for all LLM calls?
- Should we use structured output (JSON schemas) to constrain generation?

### 5. Business Outcome Evaluation

- Should there be explicit "coverage mapping" artifacts showing which requirements are addressed by which capabilities/stories?
- Should we generate a traceability matrix as a separate artifact?
- Should stories include a `businessOutcome` or `enablesGoal` field?

### 6. Recommendations (To Validate After Testing)

1. Each artifact should have **explicit ID references** to its parent layer
2. PRD generation should follow **RPG template strictly**
3. ArchiMate XML should include **relationship elements** for cross-layer tracing
4. Generate a **traceability matrix** artifact: Requirement → Goal → Capability → Application → Story

---

## Test Results

### Test Execution: 2026-01-20

**Job ID**: `job_20260120-133242_6a9240be`
**Execution ID**: `1237398`
**Duration**: 533.8 seconds (~9 minutes)
**Status**: All artifacts generated (error only on Software Delivery trigger - env var access issue)

### Test Input
```json
{
  "requirements": "Build a simple task management API that allows users to create, read, update, and delete tasks. Each task should have a title, description, status (pending, in-progress, done), and due date. Include user authentication with JWT tokens. The API should be RESTful and include proper error handling.",
  "projectName": "Task Management API v3"
}
```

### Artifacts Generated
- [x] BRD - Business requirements with objectives, stakeholders, constraints
- [x] Business Architecture - Business processes (5 elements)
- [x] Application Architecture - Application components (7 elements)
- [x] Data Architecture - Data objects (2 elements) + Data stores (2 elements)
- [x] Infrastructure Architecture - Technology services, nodes, networks
- [x] ArchiMate XML (Combined) - All layers in single importable XML
- [x] Risk Assessment - Risk markdown document
- [x] Solution Package - 6 artifacts (solution architecture, API specs, etc.)
- [x] QA Package - 2 artifacts (test strategy, test scenarios)
- [x] PRD - Product Requirements Document in markdown

### Gap Analysis

| Aspect | Expected | Actual | Gap | Severity |
|--------|----------|--------|-----|----------|
| RPG PRD Format | Full compliance with template | Partial - has sections but not detailed | **Major** | High |
| ArchiMate Conformance | Archi-importable XML | ✅ Proper namespaces, element types | None | - |
| Traceability | Explicit ID chain | Implicit via naming only | **Major** | High |
| Determinism | temperature=0, seed=42 | ✅ Already configured | None | - |
| Relationships | Cross-layer ArchiMate relationships | ❌ No `<relationship>` elements | Medium | Medium |

### Detailed Findings

#### 1. RPG PRD Format - GAPS IDENTIFIED

**Expected Structure (from template):**
- `<functional-decomposition>` with Capabilities → Features (Inputs/Outputs/Behavior)
- `<structural-decomposition>` with Repository Structure, Module Definitions
- `<dependency-graph>` with Foundation Layer, Phase 1, Phase 2, etc.
- `<implementation-roadmap>` with Entry/Exit criteria per phase
- `<test-strategy>` with Test Pyramid, Coverage Requirements, Critical Scenarios

**Actual Output:**
- Has Problem Statement, Target Users, Success Metrics ✅
- Has Capability Tree (but shallow - no Inputs/Outputs/Behavior) ⚠️
- Has Repository Structure (basic) ⚠️
- Has Module Definitions (basic) ⚠️
- Has Dependency Chain (exists but not layered properly) ⚠️
- Has Development Phases (exists but no Entry/Exit criteria) ⚠️
- Has Test Pyramid and Coverage Requirements ✅
- Has Critical Test Scenarios ✅

**Gap**: PRD generation prompt needs to be updated to strictly follow RPG template structure.

#### 2. ArchiMate Conformance - PASSED ✅

**XML Structure:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:xsi="..." xmlns:archimate="http://www.archimatetool.com/archimate"
                 name="task-management-api-v3 Architecture" version="5.0.0">
  <folder name="Business" type="elements">
    <element xsi:type="archimate:BusinessProcess" name="..." id="..."/>
  </folder>
  <folder name="Application" type="elements">
    <element xsi:type="archimate:ApplicationComponent" name="..." id="..."/>
  </folder>
  ...
</archimate:model>
```

**Validated:**
- Proper Archi namespace (http://www.archimatetool.com/archimate)
- Correct element types (BusinessProcess, ApplicationComponent, DataObject, etc.)
- Folder organization by layer
- Unique element IDs

**Action**: Test import into Archi tool to confirm.

#### 3. Traceability - GAPS IDENTIFIED

**Expected**: Explicit ID references like `GOAL-001 → CAP-001 → APP-001 → STORY-001`

**Actual**:
- BRD objectives have IDs (1, 2, 3...)
- Architectures have element IDs (UUIDs)
- No cross-reference between layers
- PRD does not reference BRD objective IDs

**Gap**: Need to implement ID propagation across artifacts.

#### 4. ArchiMate Relationships - GAPS IDENTIFIED

**Expected**: `<relationship>` elements connecting layers
```xml
<relationship xsi:type="archimate:RealizationRelationship"
              source="app-component-id" target="business-process-id"/>
```

**Actual**: Only elements in folders, no relationship elements

**Gap**: XML generation needs to create relationships based on architectural dependencies.

---

## Recommendations

### Priority 1 (Critical for TaskMaster Integration)
1. **Update PRD generation prompt** to strictly follow RPG template structure
   - Include `<functional-decomposition>` with full Feature details
   - Include `<dependency-graph>` with proper layer ordering
   - Include `<implementation-roadmap>` with Entry/Exit criteria

### Priority 2 (Important for Traceability)
2. **Implement ID propagation** across artifacts
   - BRD objectives get stable IDs (OBJ-001, OBJ-002)
   - Capabilities reference objective IDs
   - Applications reference capability IDs
   - PRD stories reference all upstream IDs

3. **Add relationship elements to ArchiMate XML**
   - RealizationRelationship: App → Business
   - AccessRelationship: App → Data
   - ServingRelationship: Tech → App

### Priority 3 (Nice to Have)
4. **Generate traceability matrix artifact**
   - Separate JSON artifact mapping: Requirement → Goal → Capability → App → Story
   - Can be used for coverage analysis

5. **Validate ArchiMate import in Archi tool**
   - Confirm XML imports correctly
   - Document any required adjustments

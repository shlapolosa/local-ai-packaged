# ArchiMate Relationship Patterns

Source: ArchiMate 3.1 Specification + Healthcare Implementation Guide

## Overview

This document defines the correct relationship types between ArchiMate elements for healthcare architecture models.

## Relationship Rules by Layer

### Motivation Layer Relationships

| Source | Target | Relationship | Description |
|--------|--------|--------------|-------------|
| Stakeholder | Driver | Association | Stakeholder has concern |
| Driver | Goal | Influence | Driver motivates goal |
| Outcome | Goal | Realization | Outcome achieves goal |
| Assessment | Driver | Association | Assessment identifies driver |

### Strategy Layer Relationships

| Source | Target | Relationship | Description |
|--------|--------|--------------|-------------|
| CourseOfAction | Outcome | Realization | Initiative achieves outcome |
| Capability | CourseOfAction | Realization | Capability enables initiative |
| Resource | Capability | Assignment | Resource supports capability |

### Business Layer Relationships

| Source | Target | Relationship | Description |
|--------|--------|--------------|-------------|
| BusinessActor | BusinessProcess | Assignment | Actor performs process |
| BusinessProcess | Capability | Realization | Process implements capability |
| BusinessProcess | BusinessService | Realization | Process delivers service |
| BusinessService | BusinessActor | Serving | Service serves actor |
| BusinessObject | BusinessProcess | Access | Process accesses data |

### Application Layer Relationships

| Source | Target | Relationship | Description |
|--------|--------|--------------|-------------|
| ApplicationComponent | ApplicationInterface | Composition | Component owns interface |
| ApplicationInterface | ApplicationService | Assignment | Interface exposes service |
| ApplicationFunction | ApplicationService | Realization | Function implements service |
| ApplicationComponent | ApplicationFunction | Assignment | Component has function |
| ApplicationFunction | DataObject | Access | Function reads/writes data |
| ApplicationFunction | ApplicationEvent | Triggering | Function triggers event |
| ApplicationEvent | ApplicationFunction | Triggering | Event triggers function |
| ApplicationInterface | ApplicationInterface | Flow | Interface-to-interface communication |

### Cross-Layer Relationships

| Source | Target | Relationship | Description |
|--------|--------|--------------|-------------|
| ApplicationService | BusinessProcess | Serving | App serves business |
| ApplicationComponent | Capability | Realization | App realizes capability |
| DataObject | BusinessObject | Realization | App data realizes business object |

## Critical Semantic Rules

### Rule 1: Gateway Pattern
**CORRECT**: Mobile Interface → Gateway Interface → Domain Interface
**WRONG**: Mobile Component → Gateway Component

Gateway relationships flow through **Interfaces**, not Components. Use Flow relationships.

```
id-ai-mobile ─[Flow]→ id-ai-gateway ─[Flow]→ id-ai-patient
```

### Rule 2: ESB/Integration Pattern
The ESB layer sits **horizontally** between internal domains and external systems.

**CORRECT**: Domain Interface → ESB Adapter Interface → External Interface
**WRONG**: Domain Component → External Component (skipping ESB)

```
id-ai-patient ─[Flow]→ id-ai-daman-adapter ─[Flow]→ id-ai-ext-daman
```

### Rule 3: Serving Direction
ApplicationService **serves** BusinessProcess (arrow points TO business).

**CORRECT**: id-as-eligibility ─[Serving]→ id-bp-check-eligibility
**WRONG**: id-bp-check-eligibility ─[Serving]→ id-as-eligibility

### Rule 4: Realization Direction
Lower layer **realizes** higher layer (arrow points UP).

**CORRECT**: id-ac-patient ─[Realization]→ id-cap-patient-management
**WRONG**: id-cap-patient-management ─[Realization]→ id-ac-patient

### Rule 5: Access Modifiers
DataObject access should specify read/write when relevant.

```xml
<relationship identifier="id-rel-001" source="id-af-validate" target="id-do-patient" xsi:type="Access">
  <property propertyDefinitionRef="accessType"><value>read</value></property>
</relationship>
```

## Traceability Chain

A complete architecture should have traceable chains from motivation to implementation:

```
Stakeholder ─[Association]→ Driver ─[Influence]→ Goal
                                                  ↑
                                    Outcome ─[Realization]┘
                                      ↑
                        CourseOfAction ─[Realization]┘
                              ↑
                   Capability ─[Realization]┘
                        ↑
            BusinessProcess ─[Realization]┘
                   ↑
      ApplicationService ─[Serving]┘
```

## Relationship ID Naming

All relationships use sequential IDs: `id-rel-001`, `id-rel-002`, etc.

## Validation Checklist

- [ ] All relationship source elements exist
- [ ] All relationship target elements exist
- [ ] Gateway flows use Interface-to-Interface
- [ ] ESB layer not skipped for external integrations
- [ ] Serving relationships point TO business layer
- [ ] Realization relationships point UP the stack
- [ ] Traceability chains are complete

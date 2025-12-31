# ArchiMate 3.1 Quick Reference

## Element Layers

### Strategy Layer
| Element | Description | Icon |
|---------|-------------|------|
| Resource | Asset required for capability | Rectangle |
| Capability | Ability to achieve outcome | Rounded rectangle |
| Value Stream | Sequence creating value | Arrow with stages |
| Course of Action | Approach to achieve goal | Rounded rectangle with arrow |

### Business Layer
| Element | Description | Notation |
|---------|-------------|----------|
| Business Actor | Individual or organization | Yellow stick figure |
| Business Role | Responsibility of actor | Yellow circle with head |
| Business Collaboration | Aggregate of roles | Yellow overlapping circles |
| Business Interface | Point of access to service | Yellow lollipop |
| Business Process | Sequence of behaviors | Yellow rounded rectangle with arrow |
| Business Function | Collection of behavior | Yellow rounded rectangle |
| Business Interaction | Unit of collective behavior | Yellow rounded rectangle with line |
| Business Event | State change that triggers | Yellow arrow shape |
| Business Service | Unit of functionality | Yellow rectangle with top line |
| Business Object | Passive element | Yellow rectangle |
| Contract | Formal agreement | Yellow rectangle with fold |
| Representation | Perceptible form of info | Yellow document |
| Product | Coherent services/contracts | Yellow box with inner rectangle |

### Application Layer
| Element | Description | Notation |
|---------|-------------|----------|
| Application Component | Modular, deployable unit | Blue box |
| Application Collaboration | Aggregate of components | Blue overlapping boxes |
| Application Interface | Point of access | Blue lollipop |
| Application Function | Internal behavior unit | Blue rounded rectangle |
| Application Process | Sequence of behaviors | Blue rounded rectangle with arrow |
| Application Interaction | Unit of joint behavior | Blue rounded rectangle with line |
| Application Event | State change | Blue arrow shape |
| Application Service | Unit of functionality | Blue rectangle with top line |
| Data Object | Data element | Blue rectangle |

### Technology Layer
| Element | Description | Notation |
|---------|-------------|----------|
| Node | Computational resource | Green 3D box |
| Device | Physical IT resource | Green 3D box with base |
| System Software | Software on node | Green parallelogram |
| Technology Collaboration | Aggregate of nodes | Green overlapping boxes |
| Technology Interface | Point of access | Green lollipop |
| Technology Function | Technology behavior | Green rounded rectangle |
| Technology Process | Sequence of tech behaviors | Green rounded rectangle with arrow |
| Technology Interaction | Joint tech behavior | Green rounded rectangle with line |
| Technology Event | Tech state change | Green arrow |
| Technology Service | Tech functionality | Green rectangle with top line |
| Artifact | Piece of data | Green document |
| Communication Network | Network infrastructure | Green pipe |
| Path | Link between nodes | Green line |
| Distribution Network | Physical distribution | Green dashed pipe |

### Physical Layer
| Element | Description |
|---------|-------------|
| Equipment | Physical machines |
| Facility | Physical structure |
| Distribution Network | Physical transport |
| Material | Physical matter |

### Motivation Layer
| Element | Description |
|---------|-------------|
| Stakeholder | Individual with interest |
| Driver | External or internal factor |
| Assessment | Result of analysis |
| Goal | End state to achieve |
| Outcome | End result of goal |
| Principle | Intended property |
| Requirement | Statement of need |
| Constraint | Restriction |
| Meaning | Knowledge interpretation |
| Value | Relative worth |

### Implementation Layer
| Element | Description |
|---------|-------------|
| Work Package | Series of actions |
| Deliverable | Precisely defined result |
| Implementation Event | State change in implementation |
| Plateau | Stable architecture state |
| Gap | Outcome of gap analysis |

## Relationship Types

### Structural Relationships
| Relationship | Description | Direction |
|-------------|-------------|-----------|
| Composition | Part-of (strong) | Whole → Part |
| Aggregation | Part-of (weak) | Whole → Part |
| Assignment | Allocation of responsibility | Assigned → Assignee |
| Realization | Making concrete | Realizing → Realized |

### Dependency Relationships
| Relationship | Description | Direction |
|-------------|-------------|-----------|
| Serving | Provides functionality | Provider → Consumer |
| Access | Use of business/data object | Accessor → Object |
| Influence | Affects another element | Influencer → Influenced |

### Dynamic Relationships
| Relationship | Description | Direction |
|-------------|-------------|-----------|
| Triggering | Temporal/causal | Trigger → Triggered |
| Flow | Transfer of object | From → To |

### Other Relationships
| Relationship | Description | Direction |
|-------------|-------------|-----------|
| Specialization | More specific type | Specific → General |
| Association | Unspecified relationship | Either direction |
| Junction | AND/OR connector | Multiple connections |

## ADOIT Excel Column Notation

### Relationship Columns
```
Composition (->Capability)     # This element contains target capabilities
Composition (<-Capability)     # This element is contained BY target capability
Realization (->Capability)     # This element realizes target capability
Serving (->Business Process)   # This element serves target process
Assignment (->Node)            # This element is assigned to target node
```

### Multiple Targets
```
# Semicolon-separated for multiple targets
Composition (->Capability) = "Child1; Child2; Child3"
```

## Common Patterns

### Capability Hierarchy
```
L1 Capability (Domain)
├── L2 Capability (Functional Area)
│   ├── L3 Capability (Specific)
│   │   └── L4 Capability (Detailed)
```

### Application-to-Capability Mapping
```
Application Component
    → Realization → Capability
    → Serving → Application Service
    → Assignment → Application Function
```

### Process-to-Application
```
Business Process
    → Realization → Capability
    ← Serving ← Application Service
```

### Technology Stack
```
System Software
    → Assignment → Node
    → Assignment → Device
Application Component
    → Assignment → Node
```

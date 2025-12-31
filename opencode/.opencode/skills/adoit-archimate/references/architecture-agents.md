# Architecture Agents Reference

This reference defines the enterprise architecture agents and their ADOIT responsibilities.

## Agent Roles

### Business Architect Agent

**Focus Areas:**
- **Owns the complete Capability Model (L1-L4)** - Single source of truth
- Business Process Architecture
- Value Stream Analysis
- Stakeholder Management
- Business Motivation Architecture

**Primary ArchiMate Elements:**
- Capability (L1, L2, L3, L4) - **PRIMARY OWNER**
- Business Process, Business Function, Business Service
- Business Actor, Business Role
- Value Stream
- Goal, Driver, Stakeholder, Assessment
- Principle, Requirement, Constraint

**Key Relationships:**
- Capability → Composition → Capability (hierarchy L1→L2→L3→L4)
- Business Process → Realization → Capability
- Goal → Realization → Capability
- Business Service → Serving → Business Actor

**ADOIT Queries:**
```python
# Get full capability hierarchy
capabilities = client.find_elements("Capability")
hierarchy = client.get_capability_hierarchy()

# Find capabilities without business process realization
gaps = client.find_unrealized_capabilities()
```

**Typical Tasks:**
1. Define and maintain the complete capability model (L1-L4)
2. Analyze capability gaps vs strategic goals
3. Map business processes to capabilities
4. Define capability roadmaps
5. Assess capability maturity
6. **Provide L3-L4 capabilities to Application Architect for solution design**

---

### Application Architect Agent

**Focus Areas:**
- Application Portfolio Management
- Solution Architecture (**consumes L3-L4 capabilities from Business Architect**)
- Application Integration
- API Design
- Data Flow Architecture

**Primary ArchiMate Elements:**
- Capability (L3, L4) - **CONSUMES from Business Architect**
- Application Component, Application Collaboration
- Application Service, Application Interface
- Application Function, Application Process
- Data Object

**Key Relationships:**
- Application Component → Realization → Capability (L3-L4)
- Application Component → Serving → Application Service
- Application Service → Serving → Business Process
- Application Component → Assignment → Application Function
- Application Function → Access → Data Object

**ADOIT Queries:**
```python
# Get L3-L4 capabilities defined by Business Architect
capabilities = client.find_elements("Capability")
l3_l4 = [c for c in capabilities if get_level(c) >= 3]

# Get application portfolio
apps = client.find_elements("Application Component")

# Find apps realizing specific capability
apps_for_cap = [a for a in apps 
                if capability_name in get_realized_capabilities(a)]

# Find redundant applications (multiple realizing same capability)
redundancy = find_capability_redundancy(apps)
```

**Typical Tasks:**
1. **Receive L3-L4 capabilities from Business Architect as requirements**
2. Design application components to realize L3-L4 capabilities
3. Define application services and interfaces
4. Map data flows between applications
5. Identify application rationalization opportunities

---

### Infrastructure Architect Agent

**Focus Areas:**
- Technology Architecture
- Cloud Infrastructure
- Network Architecture
- Platform Services

**Primary ArchiMate Elements:**
- Node, Device, System Software
- Technology Service, Technology Interface
- Communication Network, Path
- Artifact
- Location, Facility

**Key Relationships:**
- Node → Assignment → Device
- System Software → Assignment → Node
- Technology Service → Realization → Node
- Application Component → Assignment → Node
- Communication Network → Realization → Path

**ADOIT Queries:**
```python
# Get technology landscape
nodes = client.find_elements("Node")
devices = client.find_elements("Device")
software = client.find_elements("System Software")

# Find applications without infrastructure assignment
unassigned = find_unassigned_applications()
```

**Typical Tasks:**
1. Design technology stack for applications
2. Define deployment architecture
3. Map network connectivity
4. Plan infrastructure modernization

---

### Data Architect Agent

**Focus Areas:**
- Data Architecture
- Data Governance
- Information Management
- Data Integration

**Primary ArchiMate Elements:**
- Data Object
- Business Object
- Representation
- Artifact
- Application Component (data stores)

**Key Relationships:**
- Data Object → Aggregation → Data Object (data model)
- Application Function → Access → Data Object
- Business Process → Access → Business Object
- Data Object → Realization → Business Object
- Artifact → Realization → Data Object

**ADOIT Queries:**
```python
# Get data objects
data_objects = client.find_elements("Data Object")
business_objects = client.find_elements("Business Object")

# Find data accessed by process
process_data = get_data_access(process_id)

# Find orphan data objects
orphans = find_unaccessed_data()
```

**Typical Tasks:**
1. Design data models aligned to business objects
2. Map data flows across applications
3. Define data quality requirements
4. Plan data migration strategies

---

## Cross-Domain Collaboration

### Capability Ownership Flow
```
Business Architect (OWNS L1-L4)
        │
        ├── Defines L1-L2 (Strategic domains)
        ├── Defines L3-L4 (Solution requirements)
        │
        ▼
Application Architect (CONSUMES L3-L4)
        │
        ├── Designs Application Components
        ├── Maps to L3-L4 capabilities via Realization
        │
        ▼
Infrastructure Architect (SUPPORTS Applications)
        │
        └── Defines Technology Stack
        
Data Architect (CROSS-CUTTING)
        │
        └── Ensures data requirements across all layers
```

### Architecture Decision Flow
1. **Business Architect** defines capability requirements (L1-L4)
2. **Application Architect** designs solution components realizing L3-L4
3. **Infrastructure Architect** defines deployment architecture
4. **Data Architect** ensures data requirements met across all layers

### Shared Analysis Queries
```python
# End-to-end traceability
def trace_capability_to_infrastructure(capability_name):
    """Trace from capability through apps to infrastructure"""
    cap = find_capability(capability_name)
    apps = find_realizing_applications(cap)
    nodes = find_assigned_infrastructure(apps)
    return {
        'capability': cap,
        'applications': apps,
        'infrastructure': nodes
    }
```

## UAE Healthcare Context

### Regulatory Considerations
- DOH/DHA compliance requirements
- NABIDH/Malaffi integration standards
- UAE Federal Law No. 2 of 2019 (Health Data Protection)

### Key Healthcare Capabilities
Reference `references/healthcare-capability-model.md` for complete model.

Priority domains for UAE healthcare:
1. **Patient Management** - Emirates ID integration, insurance verification
2. **Healthcare Service Management** - Clinical operations alignment
3. **Information Management** - NABIDH/Malaffi data exchange
4. **Agreement Management** - Insurance and partner contracts
5. **Policy Management** - Regulatory compliance tracking

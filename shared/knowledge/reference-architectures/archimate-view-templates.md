# ArchiMate View Templates

Source: ArchiMate 3.1 Specification + Healthcare Best Practices

## Standard Views

Every healthcare architecture model should include these views:

### View 1: Motivation View (id-view-motivation)
**Purpose**: Show why the initiative exists

**Elements**:
- Stakeholders (top row)
- Drivers (second row)
- Goals (third row)
- Outcomes (bottom row)

**Layout**:
```
y=0    ┌────────────┐  ┌────────────┐  ┌────────────┐
       │Stakeholder1│  │Stakeholder2│  │Stakeholder3│
       └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
             │Association    │              │
y=120  ┌─────▼──────┐  ┌─────▼──────┐  ┌────▼───────┐
       │  Driver 1  │  │  Driver 2  │  │  Driver 3  │
       └─────┬──────┘  └─────┬──────┘  └────┬───────┘
             │Influence      │              │
y=240  ┌─────▼──────┐  ┌─────▼──────┐  ┌────▼───────┐
       │   Goal 1   │  │   Goal 2   │  │   Goal 3   │
       └─────▲──────┘  └─────▲──────┘  └────▲───────┘
             │Realization    │              │
y=360  ┌─────┴──────┐  ┌─────┴──────┐  ┌────┴───────┐
       │ Outcome 1  │  │ Outcome 2  │  │ Outcome 3  │
       └────────────┘  └────────────┘  └────────────┘
```

### View 2: Strategy View (id-view-strategy)
**Purpose**: Show how objectives will be achieved

**Elements**:
- Outcomes (top, from motivation)
- Courses of Action (middle)
- Capabilities (bottom)

**Layout**:
```
y=0    ┌────────────┐  ┌────────────┐
       │ Outcome 1  │  │ Outcome 2  │
       └─────▲──────┘  └─────▲──────┘
             │Realization    │
y=120  ┌─────┴──────┐  ┌─────┴──────┐
       │   CoA 1    │  │   CoA 2    │
       └─────▲──────┘  └─────▲──────┘
             │Realization    │
y=240  ┌─────┴──────┐  ┌─────┴──────┐  ┌────────────┐
       │Capability 1│  │Capability 2│  │Capability 3│
       └────────────┘  └────────────┘  └────────────┘
```

### View 3: Capability Map (id-view-capability-map)
**Purpose**: Grid view of business capabilities

**Layout**: 3-4 column grid, L1 capabilities as group headers

```
┌─────────────────────────────────────────────────────────┐
│                  CAPABILITY MAP                          │
├─────────────────┬─────────────────┬─────────────────────┤
│ Patient Mgmt    │ Clinical Mgmt   │ Administrative      │
├─────────────────┼─────────────────┼─────────────────────┤
│ • Registration  │ • Documentation │ • Scheduling        │
│ • Eligibility   │ • Orders        │ • Billing           │
│ • Demographics  │ • Results       │ • Reporting         │
└─────────────────┴─────────────────┴─────────────────────┘
```

### View 4: Process View (id-view-process)
**Purpose**: Business process flow

**Elements**:
- BusinessActor (left column)
- BusinessProcess (flow left-to-right)
- BusinessService (below processes)

**Layout**:
```
       │ Check      │ Select     │ Book       │ Complete   │
       │ Eligibility│ Package    │ Appointment│ Screening  │
┌──────┴────────────┴────────────┴────────────┴────────────┐
│                    PROCESS FLOW                          │
└──────┬────────────┬────────────┬────────────┬────────────┘
       │            │            │            │
       ▼            ▼            ▼            ▼
   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
   │Elig Svc│  │Package │  │Booking │  │Results │
   │        │  │Service │  │Service │  │Service │
   └────────┘  └────────┘  └────────┘  └────────┘
```

### View 5: Application Architecture (id-view-application)
**Purpose**: Complete application landscape

**Layout** (Reference Architecture):
```
y=0     ┌─────────────────────────────────────────────────┐
        │              PRESENTATION LAYER                  │
        │   ┌──────────┐            ┌──────────┐          │
        │   │ Mobile   │            │ Web      │          │
        │   │ App      │            │ Portal   │          │
        │   └────┬─────┘            └────┬─────┘          │
        └────────┼───────────────────────┼────────────────┘
y=120            │                       │
        ┌────────┼───────────────────────┼────────────────┐
        │        ▼                       ▼                │
        │   ┌────────────────────────────────────┐        │
        │   │           API GATEWAY              │        │
        │   └──────────────────┬─────────────────┘        │
        │                      │   GATEWAY LAYER          │
        └──────────────────────┼──────────────────────────┘
y=240                          │
        ┌──────────────────────┼──────────────────────────┐
        │                      ▼                          │
        │   ┌────────────────────────────────────┐        │
        │   │    IDENTITY & ACCESS MANAGEMENT    │        │
        │   └────────────────────────────────────┘        │
        │                      IAM LAYER                  │
        └─────────────────────────────────────────────────┘
y=360
        ┌─────────────────────────────────────────────────┐
        │              SERVICE LAYER (DOMAINS)            │
        │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐│
        │ │Patient  │ │Provider │ │Appoint- │ │Notifi-  ││
        │ │Domain   │ │Domain   │ │ment     │ │cation   ││
        │ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘│
        └──────┼───────────┼───────────┼───────────┼──────┘
y=600          │           │           │           │
        ┌──────┼───────────┼───────────┼───────────┼──────┐
        │      ▼           ▼           ▼           ▼      │
        │ ┌─────────────────────────────────────────────┐ │
        │ │           INTEGRATION / ESB LAYER           │ │
        │ │  ┌────────┐  ┌────────┐  ┌────────┐        │ │
        │ │  │Daman   │  │Malaffi │  │EMR     │   ...  │ │
        │ │  │Adapter │  │Adapter │  │Adapter │        │ │
        │ │  └───┬────┘  └───┬────┘  └───┬────┘        │ │
        │ └──────┼───────────┼───────────┼─────────────┘ │
        └────────┼───────────┼───────────┼───────────────┘
y=720            │           │           │
        ┌────────┼───────────┼───────────┼───────────────┐
        │        ▼           ▼           ▼               │
        │   ┌────────┐  ┌────────┐  ┌────────┐          │
        │   │ Daman  │  │Malaffi │  │  EMR   │   ...    │
        │   │(Payer) │  │ (HIE)  │  │Systems │          │
        │   └────────┘  └────────┘  └────────┘          │
        │              EXTERNAL SYSTEMS LAYER            │
        └────────────────────────────────────────────────┘
```

### View 6: Integration View (id-view-integration)
**Purpose**: External system connections

**Elements**:
- Internal ApplicationComponents (left)
- Integration adapters (center)
- External systems (right)

**Layout**: Horizontal flow showing data exchange

## Node Sizing

| Element Type | Width | Height |
|--------------|-------|--------|
| ApplicationComponent | 180px | 60px |
| ApplicationInterface | 180px | 45px |
| ApplicationService | 150px | 45px |
| ApplicationFunction | 85px | 40px |
| BusinessProcess | 120px | 50px |
| BusinessActor | 100px | 80px |
| DataObject | 120px | 45px |
| Grouping | auto | auto |

## Color Palette (ArchiMate Standard)

| Layer | Element Type | Fill Color | Border |
|-------|--------------|------------|--------|
| Motivation | Stakeholder, Driver, Goal, Outcome | #CCCCFF | #9999CC |
| Strategy | Capability, CourseOfAction, Resource | #F5DEB3 | #D4B896 |
| Business | Actor, Process, Service, Object | #FFFFB5 | #CCCC8F |
| Application | Component, Function | #B5D3E7 | #8FB5CC |
| Application | Interface | #B5D3E7 | #6699AA |
| Application | Service | #FFFFB5 | #CCCC8F |
| Application | Data Object | #C9E7B5 | #99CC8F |
| Application | Event | #FFB5B5 | #CC8F8F |
| Technology | Node, Device, Network | #C9E7B5 | #99CC8F |
| External | All external elements | #D5D5D5 | #AAAAAA |

## XML View Structure

```xml
<views>
  <diagrams>
    <view identifier="id-view-motivation" xsi:type="Diagram">
      <name xml:lang="en">Motivation View</name>
      <node identifier="id-node-001" elementRef="id-sh-doh"
            x="50" y="50" w="180" h="60">
        <style>
          <fillColor r="204" g="204" b="255"/>
          <lineColor r="153" g="153" b="204"/>
        </style>
      </node>
      <!-- More nodes... -->
      <connection identifier="id-conn-001" relationshipRef="id-rel-001"
                  source="id-node-001" target="id-node-002"/>
    </view>
  </diagrams>
</views>
```

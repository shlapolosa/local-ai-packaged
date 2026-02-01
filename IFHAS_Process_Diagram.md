# IFHAS Process Diagram

```mermaid
flowchart TB
    subgraph Entry["Entry Point"]
        A[User Opens TAMM Dashboard]
    end

    subgraph Eligibility["Eligibility Check"]
        B{Check Thiqa Category<br/>via Daman API}
        B -->|C1-C4| C[Eligible - Show IFHAS Banner]
        B -->|Not C1-C4| D[Not Eligible - Hide IFHAS]
    end

    subgraph LandingPage["IFHAS Landing Page"]
        E[View Landing Page]
        E --> F[Pending Packages]
        E --> G[Upcoming Appointments]
        E --> H[Encounter History]
        E --> I[Screening Results]
        E --> J[Program Information]
        E --> K[Facility List]
    end

    subgraph Booking["Appointment Booking Flow"]
        L[Select IFHAS Package]
        M[Select Facility]
        N{Primary Care<br/>Facility?}
        N -->|Yes| O[Show PCF Notice]
        N -->|No| P[Continue]
        O --> P
        P --> Q[Select Physician<br/>Filtered by Specialty]
        Q --> R[Choose Time Slot<br/>In-Person Only]
        R --> S[Review & Confirm Booking]
        S --> T[Send to EMR]
        T --> U{Booking<br/>Success?}
        U -->|Yes| V[Booking Confirmed]
        U -->|No| W[Show Error]
    end

    subgraph Questionnaire["Pre-screening Questionnaire"]
        X{Major Package?}
        X -->|Yes| Y[Present Questionnaire]
        Y --> Z{Complete Now?}
        Z -->|Yes| AA[Fill Questionnaire]
        Z -->|No| AB[Skip - Complete Later]
        AA --> AC[Submit to Malaffi]
        X -->|No| AD[Skip Questionnaire]
    end

    subgraph Reminders["Notification Flow"]
        AE[24H Before Appointment]
        AF[1H Before Appointment]
        AE --> AG[Send Reminder]
        AF --> AG
    end

    subgraph Results["Results & Survey"]
        AH[Screening Completed at Facility]
        AH --> AI[Results Sent to Malaffi]
        AI --> AJ[Results Available in Sahatna]
        AJ --> AK[7 Days After Results]
        AK --> AL[Send Survey Nudge]
        AL --> AM[User Completes Survey]
    end

    subgraph Nudges["Proactive Nudges"]
        AN{Insurance Status?}
        AN -->|Expired C2-C4| AO[Nudge: Renew Insurance]
        AN -->|On Hold C1| AP[Nudge: Contact Daman]
        AN -->|Active| AQ{Eligible for<br/>Screening?}
        AQ -->|Yes| AR[Nudge: Book IFHAS]
        AQ -->|Expiring in 90 days| AS[Nudge: Book Before Expiry]
    end

    A --> B
    C --> E
    F --> L
    L --> M
    V --> X
    AB --> AE
    AD --> AE
    AC --> AE
```

## Process Description

### 1. Eligibility Check
- User opens TAMM Dashboard
- System checks Thiqa insurance category via Daman API
- Only C1-C4 categories are eligible for IFHAS

### 2. Landing Page
- Displays pending packages based on age/gender
- Shows upcoming appointments and history
- Provides program information and facility list

### 3. Booking Flow
- User selects package → facility → physician → time slot
- Physicians filtered by specialties required for selected package
- Only in-person appointments available
- Booking sent to facility EMR

### 4. Pre-screening Questionnaire
- Required for Major packages only
- Can be completed immediately or skipped for later
- Results submitted to Malaffi for physician access

### 5. Notifications
- Automated reminders at 24H and 1H before appointment
- Survey nudge 7 days after results available

### 6. Proactive Nudges
- Insurance renewal reminders
- Screening availability notifications
- Pre-expiry booking encouragement

# IFHAS Use Case Sequence Diagrams

## UC1: Check User Eligibility

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant T as TAMM Dashboard
    participant S as Sahatna Backend
    participant D as Daman API

    U->>T: Open TAMM Dashboard
    T->>S: Request IFHAS Status (EID)
    S->>D: GET /member/eligibility (EID)
    D-->>S: Member Details Response
    Note over D,S: Card Number, Thiqa Category,<br/>Enrollment Date, Expiry Date,<br/>Member Status

    alt Thiqa C1-C4 & Active
        S-->>T: Eligible = true
        T-->>U: Display IFHAS Banner & Quick Tool
    else Not C1-C4 or Inactive
        S-->>T: Eligible = false
        T-->>U: Hide IFHAS Components
    end
```

---

## UC2: View IFHAS Landing Page

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant SA as Sahatna App
    participant BE as Sahatna Backend
    participant D as Daman API
    participant ST as Strapi CMS

    U->>SA: Navigate to IFHAS Landing

    par Fetch User Data
        SA->>BE: Get Pending Packages
        BE->>D: GET /member/ifhas-history (EID)
        D-->>BE: IFHAS History (5 years)
        BE-->>SA: Available Packages by Age/Gender
    and Fetch CMS Content
        SA->>BE: Get Landing Content
        BE->>ST: GET /ifhas-content
        ST-->>BE: Benefits, FAQs, Tips, Offerings
        BE-->>SA: CMS Content
    end

    SA-->>U: Render Landing Page
    Note over U,SA: Pending Packages, Upcoming Appointments,<br/>History, Results, Program Info, Facility List
```

---

## UC3: Get Available IFHAS Packages

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant SA as Sahatna App
    participant BE as Sahatna Backend
    participant D as Daman API
    participant DB as Package Config DB

    U->>SA: View Available Packages
    SA->>BE: Get Packages for User (EID)

    BE->>D: GET /member/details (EID)
    D-->>BE: Age, Gender, Insurance Status

    BE->>D: GET /member/ifhas-history (EID)
    D-->>BE: Completed Packages & Dates

    BE->>DB: Query Package Rules
    DB-->>BE: Age/Gender/Frequency Rules

    Note over BE: Calculate Eligible Packages:<br/>- Filter by age range<br/>- Filter by gender<br/>- Check frequency (not done in period)

    BE-->>SA: Available Packages List
    SA-->>U: Display Package Cards
    Note over U,SA: Major Package, Minor Package,<br/>with descriptions and eligibility status
```

---

## UC4: View IFHAS Information & History

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant SA as Sahatna App
    participant BE as Sahatna Backend
    participant D as Daman API
    participant ADB as Appointment DB

    U->>SA: View My IFHAS Info

    par Get Insurance Status
        SA->>BE: Get Insurance Details
        BE->>D: GET /member/details (EID)
        D-->>BE: Thiqa Category, Status, Expiry
        BE-->>SA: Insurance Info
    and Get IFHAS History
        SA->>BE: Get IFHAS History
        BE->>D: GET /member/ifhas-history (EID)
        D-->>BE: Past Packages (5 years)
        Note over D,BE: Authorization Date, Service Code,<br/>Provider License, Physician License
        BE-->>SA: Encounter History
    and Get Upcoming Appointments
        SA->>BE: Get Appointments
        BE->>ADB: Query IFHAS Appointments
        ADB-->>BE: Scheduled Appointments
        BE-->>SA: Upcoming List
    end

    SA-->>U: Display IFHAS Dashboard
    Note over U,SA: Insurance Card, History Timeline,<br/>Upcoming Appointments
```

---

## UC5: View Screening Results

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant SA as Sahatna App
    participant BE as Sahatna Backend
    participant M as Malaffi HIE

    U->>SA: View Screening Results
    SA->>BE: Get IFHAS Results (EID)

    BE->>M: GET /patient/encounters (EID)
    Note over BE,M: Filter: Visit Description = "ICS"<br/>(IFHAS Comprehensive Screening)
    M-->>BE: IFHAS Encounters List

    loop For Each IFHAS Encounter
        BE->>M: GET /encounter/results (Visit ID)
        M-->>BE: Lab Results, Observations
    end

    BE-->>SA: Compiled Results
    SA-->>U: Display Results by Package

    Note over U,SA: Results grouped by:<br/>- CVD Screening<br/>- Cancer Screening<br/>- Mental Health<br/>- Oral Health<br/>- Fertility Health

    alt Results Not Yet Available
        SA-->>U: "Results pending - check back later"
    end
```

---

## UC6: Book IFHAS Appointment

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant SA as Sahatna App
    participant BE as Sahatna Backend
    participant D as Daman API
    participant A as Accela Licensing
    participant E as Facility EMR

    %% Step 1: Select Package
    U->>SA: Select IFHAS Package
    SA->>BE: Get Package Details
    BE-->>SA: Specialties Required, Description

    %% Step 2: Get Facilities
    U->>SA: Browse Facilities
    SA->>BE: Get IFHAS Facilities
    BE->>A: GET /facilities?service=IFHAS
    A-->>BE: Licensed IFHAS Providers
    BE-->>SA: Facility List with Details
    SA-->>U: Display Facility Cards

    %% Step 3: Select Facility & Physician
    U->>SA: Select Facility
    SA->>BE: Get Physicians (Facility, Specialties)
    BE->>E: GET /physicians?specialty={list}
    E-->>BE: Available Physicians
    BE-->>SA: Physician List
    SA-->>U: Display Physician Cards

    %% Step 4: Get Slots
    U->>SA: Select Physician
    SA->>BE: Get Available Slots
    BE->>E: GET /slots?physician={id}&type=in-person
    E-->>BE: Available Time Slots
    BE-->>SA: Slot Calendar
    SA-->>U: Display Available Times

    %% Step 5: Confirm Booking
    U->>SA: Select Slot & Confirm
    SA->>BE: Create Appointment
    BE->>D: POST /authorization (Package Code)
    D-->>BE: Authorization Approved
    BE->>E: POST /appointments
    E-->>BE: Appointment Confirmed
    BE-->>SA: Booking Success
    SA-->>U: Show Confirmation
    Note over U,SA: Appointment ID, Date/Time,<br/>Facility, Physician, Package
```

---

## UC7: Fill Pre-screening Questionnaire

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant SA as Sahatna App
    participant BE as Sahatna Backend
    participant ST as Strapi CMS
    participant M as Malaffi HIE

    Note over U,SA: Triggered after Major Package booking

    SA->>BE: Get Questionnaire
    BE->>ST: GET /ifhas-questionnaire
    ST-->>BE: Questions (DOH-defined)
    BE-->>SA: Questionnaire Form

    alt Complete Now
        SA-->>U: Present Questionnaire
        U->>SA: Fill Answers
        U->>SA: Submit Questionnaire
        SA->>BE: POST /questionnaire/submit
        BE->>M: Submit Pre-screening Data
        Note over BE,M: HL7 ORU Message with<br/>Patient Visit ID (PV1-19)
        M-->>BE: Submission Confirmed
        BE-->>SA: Success
        SA-->>U: "Questionnaire submitted"
    else Skip for Later
        U->>SA: Skip
        SA->>BE: Mark as Pending
        BE-->>SA: Saved as Draft
        SA-->>U: "Complete before appointment"

        Note over U,SA: Questionnaire accessible from:<br/>- Landing Page<br/>- Appointment Details<br/>- Notifications
    end

    Note over M: Questionnaire results available<br/>to physician via Malaffi
```

---

## UC8: View IFHAS Facility Details

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant SA as Sahatna App
    participant BE as Sahatna Backend
    participant A as Accela Licensing
    participant PDB as Provider DB

    U->>SA: Explore IFHAS Facilities
    SA->>BE: Get Facility List

    BE->>PDB: Query Cached Facilities
    Note over BE,PDB: Synced daily from Accela
    PDB-->>BE: IFHAS Facility List

    BE-->>SA: Facilities with Basic Info
    SA-->>U: Display Facility Cards
    Note over U,SA: Name, Location, Distance,<br/>Rating, Services

    U->>SA: Select Facility
    SA->>BE: Get Facility Details (License #)

    BE->>PDB: Query Facility Profile
    PDB-->>BE: Full Details

    BE->>A: GET /facility/{licenseNo}
    A-->>BE: Current License Status

    BE-->>SA: Facility Profile
    SA-->>U: Display Details Page
    Note over U,SA: Address, Contact, Hours,<br/>Services, Physicians, Map,<br/>IFHAS Packages Offered

    opt User is PCF Registered Here
        SA-->>U: Highlight "Your Primary Care Facility"
    end
```

---

## UC9: Send Reminders & Nudges

```mermaid
sequenceDiagram
    autonumber
    participant SCH as Scheduler Service
    participant NE as Nudge Engine
    participant DB as Appointment DB
    participant D as Daman API
    participant NS as Notification Service
    participant FB as Firebase
    participant U as User Device

    Note over SCH,U: Scheduled Job runs periodically

    %% Appointment Reminders
    rect rgb(230, 245, 255)
        Note over SCH,U: Appointment Reminder Flow
        SCH->>DB: Query appointments (next 24H)
        DB-->>SCH: Upcoming Appointments

        loop Each Appointment
            SCH->>NE: Check reminder status
            alt 24H Reminder Not Sent
                NE->>NS: Send 24H Reminder
                NS->>FB: Push Notification
                FB-->>U: "Your IFHAS appointment is tomorrow"
            else 1H Reminder Not Sent
                NE->>NS: Send 1H Reminder
                NS->>FB: Push Notification
                FB-->>U: "Your IFHAS appointment is in 1 hour"
            end
        end
    end

    %% Insurance Status Nudges
    rect rgb(255, 243, 224)
        Note over SCH,U: Insurance Status Nudge Flow
        SCH->>D: GET /members/status-changes
        D-->>SCH: Members with status updates

        loop Each Member
            alt Insurance Expired (C2-C4)
                NE->>NS: Send Renewal Nudge
                NS->>FB: Push Notification
                FB-->>U: "Your Thiqa insurance has expired"
            else Insurance On Hold (C1)
                NE->>NS: Send Contact Daman Nudge
                NS->>FB: Push Notification
                FB-->>U: "Your insurance is on hold"
            else Expiring in 90 Days
                NE->>NS: Send Book Before Expiry
                NS->>FB: Push Notification
                FB-->>U: "Book your IFHAS before insurance expires"
            end
        end
    end

    %% Eligibility Nudges
    rect rgb(232, 245, 233)
        Note over SCH,U: New Eligibility Nudge Flow
        SCH->>NE: Check new eligible users
        NE->>D: Query eligible not booked
        D-->>NE: Eligible Users List

        loop Each Eligible User
            NE->>NS: Send Booking Nudge
            NS->>FB: Push Notification
            FB-->>U: "You're eligible for IFHAS screening"
        end
    end
```

---

## UC10: Post-Appointment Survey

```mermaid
sequenceDiagram
    autonumber
    participant SCH as Scheduler Service
    participant BE as Sahatna Backend
    participant M as Malaffi HIE
    participant NS as Notification Service
    participant U as User
    participant SA as Sahatna App
    participant DB as Survey DB

    Note over SCH,DB: Triggered 7 days after results available

    SCH->>BE: Check completed IFHAS visits
    BE->>M: Query recent IFHAS encounters
    M-->>BE: Encounters with results

    loop Each Completed Visit
        BE->>DB: Check survey status
        alt Survey Not Sent & 7+ Days Since Results
            BE->>NS: Trigger Survey Nudge
            NS-->>U: Push: "Share your IFHAS experience"
        end
    end

    U->>SA: Open Survey Notification
    SA->>BE: Get Survey Questions
    Note over BE: Questions defined by DOH
    BE-->>SA: Survey Form
    SA-->>U: Display Survey

    U->>SA: Complete Survey
    SA->>BE: POST /survey/submit
    BE->>DB: Store Survey Response
    DB-->>BE: Saved
    BE-->>SA: Thank You
    SA-->>U: "Thank you for your feedback"

    Note over DB: Survey data available to<br/>DOH Data Team Dashboard
```

---

## End-to-End Journey: Complete IFHAS Flow

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant T as TAMM
    participant SA as Sahatna
    participant D as Daman
    participant A as Accela
    participant E as EMR
    participant M as Malaffi
    participant N as Notifications

    rect rgb(255, 248, 225)
        Note over U,N: Discovery & Eligibility
        U->>T: Open Dashboard
        T->>SA: Check IFHAS Eligibility
        SA->>D: Verify Thiqa C1-C4
        D-->>SA: Eligible + History
        SA-->>T: Show IFHAS Banner
        T-->>U: Click to proceed
    end

    rect rgb(225, 245, 254)
        Note over U,N: Package Selection
        U->>SA: Open IFHAS Landing
        SA->>D: Get available packages
        D-->>SA: Pending packages
        SA-->>U: Display Major/Minor options
        U->>SA: Select Major Package
    end

    rect rgb(232, 245, 233)
        Note over U,N: Facility & Booking
        SA->>A: Get IFHAS facilities
        A-->>SA: Licensed providers
        SA-->>U: Show facility list
        U->>SA: Select facility
        SA->>E: Get physicians & slots
        E-->>SA: Available options
        SA-->>U: Show calendar
        U->>SA: Confirm booking
        SA->>E: Create appointment
        E-->>SA: Confirmed
        SA-->>U: Booking success
    end

    rect rgb(243, 229, 245)
        Note over U,N: Questionnaire
        SA-->>U: Present questionnaire
        U->>SA: Complete & submit
        SA->>M: Send to Malaffi
        M-->>SA: Stored for physician
    end

    rect rgb(255, 243, 224)
        Note over U,N: Reminders
        N-->>U: 24H reminder
        N-->>U: 1H reminder
    end

    rect rgb(252, 228, 236)
        Note over U,N: Screening & Results
        Note over U,E: User visits facility
        E->>M: Submit results (ICS tag)
        U->>SA: Check results
        SA->>M: Fetch by Visit ID
        M-->>SA: Lab results
        SA-->>U: Display results
    end

    rect rgb(230, 230, 230)
        Note over U,N: Feedback
        N-->>U: Survey nudge (7 days)
        U->>SA: Complete survey
        SA-->>U: Thank you
    end
```

---

## Legend

| Symbol | Meaning |
|--------|---------|
| `->>`  | Synchronous request |
| `-->>` | Response |
| `par`  | Parallel execution |
| `alt`  | Alternative paths |
| `loop` | Repeated operation |
| `opt`  | Optional step |
| `rect` | Grouped steps |
| `Note` | Additional context |

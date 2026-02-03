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

    %% Step 1: Thiqa Category Check (Yes/No)
    S->>D: GET /member/thiqa-status (EID)
    D-->>S: Thiqa Status Response
    Note over D,S: Card Number, Thiqa Category,<br/>Enrollment Date, Expiry Date,<br/>Member Status

    alt Is Thiqa Patient (C1-C4) & Active
        Note over S: User IS a Thiqa patient

        %% Step 2: Get Pending Screenings (separate step)
        S->>D: GET /member/pending-screenings (EID)
        D-->>S: Pending IFHAS Packages

        alt Has Pending Screenings
            S-->>T: Thiqa = true, HasPending = true
            T-->>U: Display IFHAS Banner + Quick Tool Tile
            Note over T,U: Banner shows pending screenings<br/>Tile always visible for Thiqa users
        else No Pending Screenings
            S-->>T: Thiqa = true, HasPending = false
            T-->>U: Display Quick Tool Tile only (no Banner)
            Note over T,U: Tile always visible for Thiqa users<br/>Banner only when pending screenings exist
        end
    else Not Thiqa (C1-C4) or Inactive
        S-->>T: Thiqa = false
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

    Note over SA,D: TRANSACTIONAL Experience (NEW)<br/>Previously: Informational only via CMS<br/>Now: User-specific eligibility, packages, results

    par Fetch User Data (Transactional - from Daman)
        SA->>BE: Get Pending Packages
        BE->>D: GET /member/ifhas-history (EID)
        D-->>BE: IFHAS History (5 years)
        Note over D,BE: User-specific pending screenings<br/>tailored to THIS user's status
        BE-->>SA: Available Packages by Age/Gender
    and Fetch CMS Content (Informational - static)
        SA->>BE: Get Landing Content
        BE->>ST: GET /ifhas-content
        ST-->>BE: Benefits, FAQs, Tips, Offerings
        Note over ST,BE: Static content for display only
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
    participant PP as Provider Portal Config
    participant ST as Strapi CMS

    U->>SA: View Available Packages
    SA->>BE: Get Packages for User (EID)

    BE->>D: GET /member/details (EID)
    D-->>BE: Age, Gender, Insurance Status

    BE->>D: GET /member/ifhas-history (EID)
    D-->>BE: Eligible Bundle IDs (e.g., 5221, 5223)
    Note over D,BE: Daman returns Bundle ID codes<br/>e.g., "5221" = Comprehensive Screening Major

    %% CPT Code Mapping (two scenarios)
    alt Scenario A: Daman sends Bundle ID + CPT Codes (PREFERRED)
        Note over D,BE: If Daman agrees to send CPT codes<br/>with bundle IDs → Dynamic mapping
        BE->>ST: Map CPT codes to descriptions
        ST-->>BE: Package names, descriptions (AR/EN)
    else Scenario B: Daman sends Bundle ID only (CURRENT)
        Note over D,BE: If Daman only sends bundle ID<br/>→ Manual mapping required
        BE->>PP: GET /bundle-cpt-mapping
        PP-->>BE: Bundle ID → CPT codes mapping
        Note over PP,BE: Mapping maintained by business<br/>in Provider Portal (like Azure Admin)
        BE->>ST: Map CPT codes to descriptions
        ST-->>BE: Package names, descriptions (AR/EN)
    end

    BE->>PP: Query Package Rules
    PP-->>BE: Age/Gender/Frequency Rules, Specialty Mappings

    Note over BE: Calculate Eligible Packages:<br/>- Filter by age range<br/>- Filter by gender<br/>- Check frequency (not done in period)<br/>- Group by specialty for bundling

    BE-->>SA: Available Packages List
    SA-->>U: Display Package Cards
    Note over U,SA: Major AND Minor Packages can be selected together<br/>(bundled if same specialty)<br/>with descriptions and eligibility status
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

    Note over SA,D: Daman is SOURCE OF TRUTH<br/>Data fetched fresh every time<br/>(eligibility can change daily)

    par Get Insurance Status (fresh from Daman)
        SA->>BE: Get Insurance Details
        BE->>D: GET /member/details (EID)
        D-->>BE: Thiqa Category, Status, Expiry
        Note over D,BE: Always fetch fresh -<br/>status can change daily
        BE-->>SA: Insurance Info
    and Get IFHAS History (fresh from Daman)
        SA->>BE: Get IFHAS History
        BE->>D: GET /member/ifhas-history (EID)
        D-->>BE: Past Packages (5 years)
        Note over D,BE: Authorization Date, Service Code,<br/>Provider License, Physician License
        BE-->>SA: Encounter History
    and Get Upcoming Appointments (local)
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

    Note over BE,M: ⚠️ MECHANISM TBD<br/>Exact approach for retrieving results<br/>by Visit ID needs alignment with<br/>Malaffi Clinical & Data teams

    BE->>M: GET /patient/encounters (EID)
    Note over BE,M: Filter: Visit Description = "ICS"<br/>(IFHAS Comprehensive Screening)<br/><br/>Challenge: Need mechanism to identify<br/>which results belong to which package/visit

    M-->>BE: IFHAS Encounters List

    loop For Each IFHAS Encounter
        BE->>M: GET /encounter/results (Visit ID)
        Note over BE,M: Grouping mechanism TBD:<br/>How to map results to specific<br/>packages within a visit
        M-->>BE: Lab Results, Observations
    end

    Note over BE: Depends on facilities sending<br/>results back to Malaffi

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
    participant PP as Provider Portal Config
    participant A as Accela Licensing
    participant E as Facility EMR

    %% Step 0: Re-verify Eligibility (required every time - can change daily)
    SA->>BE: Verify Current Eligibility
    BE->>D: GET /member/pending-screenings (EID)
    D-->>BE: Current Eligible Packages
    Note over D,BE: Eligibility checked on EVERY interaction<br/>Daman is source of truth (can change daily)

    %% Step 1: Select Package
    U->>SA: Select IFHAS Package(s)
    Note over U,SA: User can select Major AND Minor<br/>packages together (bundled by specialty)
    SA->>BE: Get Package Details
    BE->>PP: Get Package Configuration
    PP-->>BE: Specialties, Facility Mappings
    Note over PP,BE: Provider Portal defines:<br/>- Specialty-to-Package mapping<br/>- Facility-to-Package mapping
    BE-->>SA: Specialties Required, Description

    %% Step 2: Get Facilities (filtered by selected package)
    U->>SA: Browse Facilities
    SA->>BE: Get IFHAS Facilities for Package
    BE->>A: GET /facilities?service=IFHAS
    A-->>BE: Licensed IFHAS Providers
    BE->>PP: Get Facility-Package Mapping
    PP-->>BE: Facilities offering this Package
    Note over BE,PP: Not all packages available at all facilities<br/>(e.g., cancer screening needs special equipment)
    BE-->>SA: Filtered Facility List
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
    participant PP as Provider Portal Config
    participant ST as Strapi CMS
    participant M as Malaffi HIE

    Note over U,SA: Triggered after booking - if package requires questionnaire

    %% Check if questionnaire required (configurable per package)
    SA->>BE: Check Questionnaire Requirement
    BE->>PP: GET /package/{id}/config
    PP-->>BE: Package Config (questionnaire_required: true/false)
    Note over PP,BE: Questionnaire requirement is CONFIGURABLE<br/>per package (not hardcoded to Major only)<br/>Allows future flexibility

    alt Questionnaire Required for this Package
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
            Note over U,SA: Valid from appointment confirmation<br/>until MINUTES before appointment<br/><br/>Accessible from:<br/>- Landing Page<br/>- Appointment Details<br/>- Reminder Notifications
        end

        Note over M: Questionnaire results available<br/>to physician via Malaffi
    else No Questionnaire Required
        SA-->>U: Proceed without questionnaire
    end
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
    participant QDB as Questionnaire DB
    participant D as Daman API
    participant NS as Notification Service
    participant FB as Firebase
    participant U as User Device

    Note over SCH,U: Scheduled Job runs periodically

    %% Questionnaire Completion Reminders (NEW)
    rect rgb(255, 240, 245)
        Note over SCH,U: Questionnaire Reminder Flow (NEW)<br/>Reminders to complete pre-screening questionnaire
        SCH->>DB: Query appointments (next 24H)
        DB-->>SCH: Upcoming Appointments
        SCH->>QDB: Check questionnaire completion status
        QDB-->>SCH: Pending Questionnaires

        loop Each Appointment with Pending Questionnaire
            SCH->>NE: Check questionnaire reminder status
            alt 24H Reminder Not Sent & Questionnaire Incomplete
                NE->>NS: Send 24H Questionnaire Reminder
                NS->>FB: Push Notification
                FB-->>U: "Complete your pre-screening questionnaire before tomorrow's appointment"
            else 1H Reminder Not Sent & Questionnaire Incomplete
                NE->>NS: Send 1H Questionnaire Reminder
                NS->>FB: Push Notification
                FB-->>U: "Your appointment is in 1 hour - please complete your questionnaire now"
            end
        end
    end

    %% Appointment Reminders (EXISTING - already implemented)
    rect rgb(230, 245, 255)
        Note over SCH,U: Appointment Reminder Flow (EXISTING)
        SCH->>DB: Query appointments (next 24H)
        DB-->>SCH: Upcoming Appointments

        loop Each Appointment
            SCH->>NE: Check appointment reminder status
            alt 24H Appointment Reminder Not Sent
                NE->>NS: Send 24H Appointment Reminder
                NS->>FB: Push Notification
                FB-->>U: "Your IFHAS appointment is tomorrow"
            else 1H Appointment Reminder Not Sent
                NE->>NS: Send 1H Appointment Reminder
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
    participant PP as Provider Portal
    participant D as Daman
    participant A as Accela
    participant E as EMR
    participant M as Malaffi
    participant N as Notifications

    rect rgb(255, 248, 225)
        Note over U,N: Discovery & Eligibility (2-step check)
        U->>T: Open Dashboard
        T->>SA: Check IFHAS Eligibility
        SA->>D: Step 1: Is Thiqa patient? (Yes/No)
        D-->>SA: Thiqa Status
        SA->>D: Step 2: Get pending screenings
        D-->>SA: Pending packages (if Thiqa=Yes)
        alt Has Pending Screenings
            SA-->>T: Show IFHAS Banner + Tile
        else Thiqa but No Pending
            SA-->>T: Show Tile only (no Banner)
        end
        T-->>U: Click to proceed
    end

    rect rgb(225, 245, 254)
        Note over U,N: Package Selection
        U->>SA: Open IFHAS Landing
        SA->>D: Get available packages (Bundle IDs)
        D-->>SA: Bundle IDs (e.g., 5221)
        SA->>PP: Map to CPT codes & descriptions
        PP-->>SA: Package details
        SA-->>U: Display Major AND Minor options
        U->>SA: Select packages (can select both)
        Note over U,SA: Bundled by specialty
    end

    rect rgb(232, 245, 233)
        Note over U,N: Facility & Booking
        SA->>D: Re-verify eligibility (every time)
        D-->>SA: Current status
        SA->>A: Get IFHAS facilities
        A-->>SA: Licensed providers
        SA->>PP: Filter by package-facility mapping
        PP-->>SA: Facilities offering selected package
        SA-->>U: Show filtered facility list
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
        Note over U,N: Questionnaire (if package requires)
        SA->>PP: Check if questionnaire required
        PP-->>SA: Required = true/false (configurable)
        alt Questionnaire Required
            SA-->>U: Present questionnaire
            U->>SA: Complete & submit (valid until minutes before appt)
            SA->>M: Send to Malaffi
            M-->>SA: Stored for physician
        end
    end

    rect rgb(255, 243, 224)
        Note over U,N: Reminders
        N-->>U: 24H questionnaire reminder (NEW)
        N-->>U: 1H questionnaire reminder (NEW)
        N-->>U: Appointment reminders (EXISTING)
    end

    rect rgb(252, 228, 236)
        Note over U,N: Screening & Results
        Note over U,E: User visits facility
        E->>M: Submit results (ICS tag)
        U->>SA: Check results
        SA->>M: Fetch by Visit ID (mechanism TBD)
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

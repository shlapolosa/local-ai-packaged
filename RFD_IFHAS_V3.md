Roadmap Feature Definition (RFD)

IFHAS Version 3.0

30 December 2025

sign-off trail

Document control

Terms and Abbreviations

Roadmap Item & Feature Summary

Summary

The document describes a project by the Abu Dhabi Department of Health
for IFHAS screening program. The core functionality includes providing
clear and accessible information about the importance of the IFHAS,
highlighting its benefits and the significance of preventive health
screenings. It enables booking IFHAS appointments based on user's
eligibility, reviewing the Prescreening Questionnaire, and sending
reminders for IFHAS appointments. The intended outcome is to be aware of
the available screening program by age and gender and to empower the
community to take care of their health, supporting healthy behavior and
longevity.

BACKGROUND AND CONTEXT

KEY DRIVERS

IFHAS is part of a comprehensive, periodic, and preventive screening
initiative from DOH/ADPHC, which aims to improve the health outcomes of
the citizens in the Emirate of Abu Dhabi. The program aims to provide
early detection of chronic diseases and various health conditions such
as cardiovascular diseases, mental health issues, fertility health, oral
health problems, and common cancers. By identifying these conditions
early, the program seeks to reduce complications and enable timely
preventive measures and therapeutic interventions. The program provides
various screenings for males and females as per their age.

IFHAS is offered at multiple facilities across Abu Dhabi. Sahatna will
receive the list of facilities marked as IFHAS providers from the Accela
licensing system, with the ability to enable or disable each facility
for IFHAS in the backend.

In 2024, the Thiqa C1 member engagement with the IFHAS CVD program was
low and there are minimal screenings (\~40%) being done by the
population of Abu Dhabi. The mandate is to increase engagement (on
IFHAS) by 75% by 2026. It is expected that Sahatna will help bring about
increased engagement through clear information visibility and ease of
booking screening appointments. Thus, enhancing the overall IFHAS
journey and experience by the participants.

STAKEHOLDERS

TARGET AUDIENCE

Only users holding a Thiqa insurance level from 1 to 4 are eligible to
participate in the IFHAS Program.

Scope

LIST of epics

Epic 1: Check user eligibility

Description: Check within Daman service if the user is eligible for
IFHAS screening.

Expected Outcome: If the user has Thiqa level from С1 to С4, they will
see IFHAS Banner and Quick tool on the TAMM Dashboard.

Note: There will be integration with the Daman service to check user's
eligibility. IFHAS Banner will be managed via Strapi CMS and will depend
on TAMM team.

Epic 2: IFHAS Landing page

Description: Display IFHAS Landing page for eligible users.

Expected Outcome: The IFHAS Landing page contains:

Pending packages

Book IFHAS appointment

Current and previous Screening results (only if facilities are flagging
the results as IFHAS)

History of previous packages from Daman

What is IFHAS banner

Benefits

Conditions are assessed under IFHAS

IFHAS offerings

Digital Pre-screening questionnaire using the same architecture used for
the other screenings no results would be shown

Helpful Tips

Explore facility list

FAQs

Epic 3: Available IFHAS packages

Description: Displaying available IFHAS packages for the user.

Expected Outcome: Sahatna will receive member IFHAS details based on
user EID, as well as pending packages for the user from Daman. The user
will be able to choose which package they want to book an appointment
for as listed upon age and gender.

Epic 4: View IFHAS-related information

Description: Displaying current and past IFHAS-related information.

Expected Outcome: Users can view their current IFHAS insurance
eligibility status, completed packages, and upcoming IFHAS appointments
based on DAMAN Api's data

Epic 5: View screening results

Description: Displaying screening results after IFHAS appointment.

Expected Outcome: After the screening, users can view their results on
Sahatna, with data retrieved from Malaffi (only if facilities are
flagging the appointment as IFHAS).

Note: Facility should add flag IFHAS to corresponding screenings. This
should be solved via Facility onboarding.

Epic 6: Book IFHAS appointment

Description: Eligible users can book IFHAS appointments for major or
minor packages.

Expected Outcome: The user selects IFHAS package, facility (physicians
will be auto fetched based on the business shared by DOH), and book an
appointment.

Note: Sahatna will receive the list of facilities marked as IFHAS
providers from the Accela licensing system, with the ability to enable
or disable each facility for IFHAS in the backend. The system will
filter doctors by specialties based on IFHAS packages. IFHAS appointment
can only be In-Person.

Epic 7: Fill in Pre-screening Questionnaire

Description: When a user books an IFHAS appointment for Major package,
they must fill in a digital Pre-screening Questionnaire before visiting
the doctor.

Expected Outcome: After a successful booking of IFHAS appointment for
Major package, the system shall present the pre-screening questionnaire
to the user. The user may complete the questionnaire immediately or
choose to skip it and complete it later. If skipped, the questionnaire
must remain accessible to the user at any time before the scheduled
appointment.

Note: List of questions for the Pre-screening Questionnaire should be
provided by DOH. Results of Pre-screening Questionnaire filled by the
patient will be available for physicians by Malaffi.

Epic 8: View IFHAS facility details

Description: The user can review details of the IFHAS facility.

Expected Outcome: They can explore the IFHAS facility list and review
details of a clinic.

Note: The system will display only facilities from the list provided by
DOH.

Epic 9: Send reminders

Description: Sahatna should send reminders to complete important tasks -
update insurance or book an appointment for a new screening.

Expected Outcome: Reminders after booking the appointment 24H and 1H
prior to the appointment.

Note: Nudges will be confirmed after the agreement with Daman on the
data that will be provided through APIs, below are sample nudges:

Nudge the user for the screening that were not done

If the user has Thiqa2, Thiqa3, Thiqa4 and the insurance is expired

If the user has Thiqa1 and the insurance is on hold

If the user is eligible, the system shall nudge them to Book IFHAS
appointments upon age and gender.

If the Thiqa insurance expires in 90 days, the system shall nudge the
user to book a pending IFHAS appointment.

Epic 10: Post-appointment survey

Description: After an IFHAS appointment, the system should collect user
feedback through a post-appointment survey for visits which are flagged
as IFHAS on the provider side.

Expected Outcome: 7 days (Can be configurable) after the results become
available, the system shall nudge the user to complete the survey,
encouraging them to share feedback on their experience.

Note: Questions for surveys should be provided by DOH. Dashboard to
review overall survey results for DOH business owners will be prepared
by DOH data team team.

Assumptions

For a successful implementation of the program, it is assumed that the
following will be made available by DOH

Data Availability from Daman System

Daman will make the following data elements available for Sahatna to
consume using APIs.

Member card number

THIQA category (TH1, TH2, TH3, etc.)

Member enrolment start date

Member expiry date

Member status. (Active / Expired / Cancelled)

Authorization approval date

Service description (IFHAS Package)

Service code (IFHAS Package)

Authorization Status Received date

Provider License Number (MFXXX)

Physician License Number (GDXXX)

This data will be accessible on demand.

Quality of data will be the responsibility of Daman

The integration should support seamless data flow, enabling Sahatna to
provide users with accurate information on their Thiqa category, prior
encounters, and current eligibility.

Screening Results Retrieval from Malaffi:

Diagnostic results if any will be retrieved securely and on-demand from
the Malaffi system.

The integration with Malaffi should ensure that once the screening is
completed, the results are promptly accessible to the user through the
Sahatna app.

Assumption: Screening results should have the visit identifier to
selectively filter results for IFHAS Comprehensive Screening.

IFHAS Service Identification by Facilities

Facilities offering IFHAS services must have a designated service type
or identifier within their system to differentiate IFHAS appointments
from other appointments. This will enable Sahatna to accurately list and
filter facilities based on their participation in the IFHAS program.
Note: the feasibility of implementing this requirement depends on
multiple stakeholders, including providers and Malaffi.

DOH facility licensing system

DOH is the responsible team for ensuring DOH licensing system will
include a flag for IFHAS service providers.

IFHAS Packages and screening information

Packages and corresponding screening services (codes and descriptions)
applicable to the eligible population, as defined by age- and
gender-specific eligibility criteria which would be provided by
DOH/ADPHC

List of specialties and facilities for each package should be provided
by DOH/ADPHC in case the information is not coming from Accela or Daman.

TO-BE USER JOURNEYS

User Journey: BOOK IFHAS Appointment.

The Detailed workflow can be viewed at this link.

USER JOURNEY: View Encounter History

The Detailed workflow can be viewed at this link.

USER JOURNEY: Nudge the user

The Detailed workflow can be viewed at this link.

Business Processes: Book IFHAS appointment.

Eligibility check

When the user opens the TAMM Dashboard, the system will verify their
IFHAS eligibility through the Daman service. Only users with Thiqa
categories C1--C4 are eligible for the IFHAS program.

View Landing page

On the landing page, the user can access the pending IFHAS packages
based on their eligibility, track upcoming IFHAS appointments, check
encounter history, and see their screening results. The page also allows
the user to learn about the program, explore its benefits and offerings,
browse FAQs, and review the list of IFHAS facilities.

Determine Available IFHAS Packages

The system will store DOH-provided data on IFHAS packages in the
backend, including related age ranges, gender, screening frequency, the
specialties associated with each package, and the facilities authorized
to perform the required screenings.

Using eligibility data and the user's IFHAS appointment history provided
by Daman, the system will determine which packages are currently
available to the user.

Select IFHAS package

The system will retrieve the member's IFHAS details from Daman and use
this information to determine which IFHAS packages are available based
on their gender, age, and appointment frequency. Once the available
packages are displayed, the user can select a preferred package and
proceed to book an IFHAS appointment seamlessly through the system.

Select IFHAS facility

To book an IFHAS appointment, the user must first select a facility.
Sahatna will receive the list of facilities marked as IFHAS providers
from the Accela licensing system, allowing the user to choose the most
suitable location for their appointment.

If a Primary care registered facility appears in the list of IFHAS
facilities, the user will be informed accordingly.

The list of IFHAS facilities is updated annually, as new privileges and
changes are introduced on a yearly basis.

Select physician

When the user selects a facility, the system will display a filtered
list of physicians. The filtering will take into account the specialties
required for the selected IFHAS package, ensuring that only relevant
physicians are shown. The system will display only those physicians who
have available slots for in-person appointments, as IFHAS appointments
can only be conducted in person.

Choose slot

When the user selects a physician, they can select a convenient time
slot and proceed with booking their IFHAS appointment.

Teleconsultation is not available for IFHAS appointments. In future,
Teleconsultation may be made available for follow-up appointments only.

Book IFHAS appointment

The user must review all appointment details and confirm the booking.
Once confirmed, the system will send the information to the selected
facility. After receiving a successful response from the facility, the
system will notify the user that the appointment has been booked
successfully.

Fill out IFHAS Pre-screening Questionnaire

After the IFHAS appointment is booked for the Major package, the user
must fill out the digital IFHAS pre-screening questionnaire. The user
can skip it and complete it later. If skipped, the questionnaire must
remain accessible to the user at any time before and during the
scheduled appointment.

Business Processes: View Encounter History

Check upcoming IFHAS appointments

The user can view upcoming IFHAS appointments directly on the landing
page.

Access IFHAS encounter history

The user can access the history of previously completed IFHAS packages,
as well as active packages. This information is displayed across all
IFHAS packages that the user was eligible for at different points in
time.

Review IFHAS screening results

The user can view the IFHAS screening results when they are available
from Malaffi.

Business Processes: Nudge the user

Insurance Expired

If the user has Thiqa 2, Thiqa 3, or Thiqa 4 and their insurance is
expired, the system shall display an "Insurance Expired" nudge,
informing the user that they need to contact Daman to renew their
insurance.

Insurance On Hold

If the user has Thiqa 1 and their insurance is on hold, the system shall
display an "Insurance on Hold" nudge, advising the user to contact Daman
to resolve and renew their insurance.

IFHAS Screening Available

If the user is eligible for an IFHAS package based on their age and
gender, the system shall display a nudge encouraging the user to book an
IFHAS appointment.

External Integrations: Key system/API interactions mapped to user
actions.

EMR Integration (Appointment Booking)

The IFHAS module will interact with the EMR using the existing
appointment booking services. The current integration specifications
will have to be extended to accommodate the IFHAS appointment service
types. Providers will need to include the new service types to support
the workflows envisioned. It is expected that the documentation for the
EMR integration will be updated accordingly.

Integration with Daman

The system integrates with Daman service to receive information for
users' eligibility and IFHAS history. Daman shall provide comprehensive
API for

The member details:

Member card number

THIQA category (C1, C2, C3, C4)

Member enrolment start date

Member expiry date

Member status. (Active / Expired / Cancelled)

The member IFHAS details (for last 5 years):

Authorization approval date

Service description (IFHAS Package)

Service code (IFHAS Package)

Authorization Status Received date

Provider License Number (MFXXX)

Physician License Number (GDXXX)

The activity details should be an array of records, Paginated, oldest to
earliest (Latest first), Filter by Type of Activity. Data should be
extracted for the last 5 years only.

The member IFHAS details (within the previous validity periods):

Authorization approval date

Service description (IFHAS Package)

Service code (IFHAS Package)

Authorization Status Received date

Provider License Number (MFXXX)

Physician License Number (GDXXX)

Malaffi Integration (Retrieval of IFHAS results)

The IFHAS module will also interact with the Malaffi system to retrieve
the IFHAS-specific screening reports. The integration will follow the
existing specifications to retrieve lab reports from Malaffi. The new
logic needs to be applied to identify IFHAS-related reports.

Some notes to be considered while integrating with Malaffi for IFHAS:

For Malaffi, all results are processed uniformly. There is no
result-level tagging to distinguish IFHAS reports from others;
identification occurs solely at the encounter level. Providers can
ensure correct identification of IFHAS reports by:

Sending the appropriate visit description code in the encounter data,
clear meaning indicating an IFHAS Comprehensive Screening visit.

Including the visit identifier in the HL7 message (PV1-19 field).

When both the above conditions are met, the system can accurately
identify and categorize an IFHAS report.

For IFHAS visits, providers are expected to send both a 'Visit
description' and a visit ID (Encounter) when submitting outpatient (OP)
encounters to Malaffi. While this protocol has been communicated to
providers and implemented in Malaffi's system, 100% compliance across
all facilities cannot be guaranteed. This requirement pertains to the
HL7 ORU (Observational Result) Message, which includes a segment for
encounter information. However, this segment is not mandatory,
accommodating the workflow of standalone diagnostic centers where no
formal encounter occurs.

The Visit Description tag defined for IFHAS Comprehensive Screening has
a code value of "ICS." and this value is expected from providers who
offer IFHAS services as per DOH circular (22/2023). (Compliance with
this standard may not be 100% by the providers)

DOH Licensing System Integration:

It is expected that Sahatna will extend the current integration with DOH
licensing system to include IFHAS facilities also. DOH licensing will
provide additional flags to identify facilities providing IFHAS
services. This will help in maintaining an updated list of IFHAS service
providers.

CMS Integration:

Strapi integration enables centralized management of the TAMM dashboard
banner and the IFHAS pre-screening questionnaire PDF, ensuring that
content can be updated quickly and consistently through the CMS.

To-Be UX/UI Designs IN LOW FIDELITY

Landing page

IFHAS Packages

IFHAS Offerings

Select Hospital or Clinic

CHOOSE Physician

Select slot

View PHYSICIAN PROFILE

Confirm booking

Fill out PRE-SCREENING Questionnaire

Explore IFHAS Facilities

Cancel IFHAS Appointment

Reschedule IFHAS Appointment

Nudges

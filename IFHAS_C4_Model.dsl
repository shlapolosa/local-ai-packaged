workspace "IFHAS - Integrated Family Health and Screening" "C4 Model for Abu Dhabi DOH IFHAS Program on Sahatna Platform" {

    !identifiers hierarchical

    model {
        # ==========================================
        # PEOPLE / ACTORS
        # ==========================================

        citizen = person "Abu Dhabi Citizen" "Thiqa C1-C4 insurance holder eligible for IFHAS screening" "Citizen"

        physician = person "Healthcare Physician" "Doctor at IFHAS facility performing screenings" "Physician"

        dohAdmin = person "DOH Administrator" "Department of Health staff managing IFHAS program" "Admin"

        dohDataTeam = person "DOH Data Team" "Analytics team reviewing survey results and program metrics" "Admin"

        facilityAdmin = person "Facility Administrator" "Healthcare facility staff managing appointments" "Admin"

        # ==========================================
        # EXTERNAL SYSTEMS
        # ==========================================

        group "External Systems" {
            daman = softwareSystem "Daman Insurance System" "National health insurance provider - manages Thiqa eligibility and IFHAS authorization history" "External"

            malaffi = softwareSystem "Malaffi HIE" "Abu Dhabi Health Information Exchange - stores and shares patient health records and screening results" "External"

            accela = softwareSystem "Accela Licensing System" "DOH facility licensing system - maintains list of IFHAS-authorized healthcare providers" "External"

            uaePass = softwareSystem "UAE Pass" "National digital identity platform for citizen authentication" "External"

            emrSystems = softwareSystem "Healthcare Facility EMRs" "Electronic Medical Record systems at IFHAS facilities - manages appointments and clinical data" "External"

            firebase = softwareSystem "Firebase Cloud Messaging" "Google push notification service for mobile alerts" "External"

            strapiCms = softwareSystem "Strapi CMS" "Headless content management system for IFHAS program content" "External"
        }

        # ==========================================
        # SAHATNA SYSTEM (IFHAS Module)
        # ==========================================

        sahatna = softwareSystem "Sahatna Super App" "Abu Dhabi's digital health platform enabling IFHAS screening booking, results viewing, and health engagement" "Target" {

            # --- Presentation Layer ---
            group "Presentation Layer" {
                mobileApp = container "Sahatna Mobile App" "Native mobile application for iOS and Android" "React Native" "Mobile"

                webPortal = container "Sahatna Web Portal" "Web-based access to Sahatna services" "React.js" "Web"

                tammWidget = container "TAMM Dashboard Widget" "IFHAS banner and quick tool on government portal" "Web Component" "Web"
            }

            # --- API Gateway ---
            apiGateway = container "API Gateway" "Central entry point for all client requests - handles routing, rate limiting, authentication" "Kong / AWS API Gateway" "Gateway"

            # --- Core Services ---
            group "Core Microservices" {
                identityService = container "Identity Service" "User authentication, session management, UAE Pass integration" "Node.js" "Service" {
                    authController = component "Auth Controller" "Handles login/logout requests" "Express Controller"
                    sessionManager = component "Session Manager" "JWT token management" "JWT Library"
                    uaePassAdapter = component "UAE Pass Adapter" "OAuth 2.0 integration with UAE Pass" "OAuth Client"
                }

                patientService = container "Patient Service" "Patient profile management, consent, and survey handling" "Node.js" "Service" {
                    profileController = component "Profile Controller" "Patient demographics and preferences" "Express Controller"
                    surveyController = component "Survey Controller" "Post-appointment feedback collection" "Express Controller"
                    consentManager = component "Consent Manager" "Health data sharing consent" "Business Logic"
                }

                providerService = container "Provider Service" "Healthcare facility and physician management" "Node.js" "Service" {
                    facilityController = component "Facility Controller" "IFHAS facility search and details" "Express Controller"
                    physicianController = component "Physician Controller" "Doctor profiles and availability" "Express Controller"
                    specialtyMapper = component "Specialty Mapper" "Maps IFHAS packages to medical specialties" "Business Logic"
                }

                appointmentService = container "Appointment Service" "IFHAS appointment booking and management" "Node.js" "Service" {
                    bookingController = component "Booking Controller" "Appointment CRUD operations" "Express Controller"
                    slotManager = component "Slot Manager" "Available time slot retrieval" "Business Logic"
                    appointmentTracker = component "Appointment Tracker" "Status tracking and history" "Business Logic"
                    emrGateway = component "EMR Gateway" "Integration with facility EMR systems" "HL7/REST Client"
                }

                integrationService = container "Integration Service" "External system adapters for Daman, Malaffi, Accela" "Node.js" "Service" {
                    damanAdapter = component "Daman Adapter" "Eligibility check and IFHAS history retrieval" "REST Client"
                    malaffiAdapter = component "Malaffi Adapter" "Screening results retrieval via HL7/FHIR" "HL7/FHIR Client"
                    accelaAdapter = component "Accela Adapter" "Licensed facility list synchronization" "REST Client"
                    integrationOrchestrator = component "Integration Orchestrator" "Coordinates multi-system workflows" "Saga Pattern"
                }

                phrService = container "PHR Service" "Personal Health Records - screening results and encounter history" "Node.js" "Service" {
                    resultsController = component "Results Controller" "IFHAS screening results display" "Express Controller"
                    encounterController = component "Encounter Controller" "IFHAS encounter history" "Express Controller"
                    ifhasFilter = component "IFHAS Filter" "Filters results by ICS visit code" "Business Logic"
                }

                notificationService = container "Notification Service" "Multi-channel notifications and nudge engine" "Node.js" "Service" {
                    nudgeEngine = component "Nudge Engine" "Proactive engagement rule engine" "Rule Engine"
                    pushHandler = component "Push Handler" "Firebase push notification sender" "FCM Client"
                    smsHandler = component "SMS Handler" "SMS gateway integration" "SMS Client"
                    emailHandler = component "Email Handler" "Email delivery service" "SMTP Client"
                    templateEngine = component "Template Engine" "Notification message templating" "Handlebars"
                }

                cmsService = container "CMS Service" "Content management for IFHAS program information" "Node.js" "Service" {
                    contentController = component "Content Controller" "Landing page content, FAQs, tips" "Express Controller"
                    questionnaireController = component "Questionnaire Controller" "Pre-screening questionnaire management" "Express Controller"
                    strapiClient = component "Strapi Client" "Headless CMS integration" "REST Client"
                }

                batchService = container "Batch Processing Service" "Scheduled jobs for sync and reminders" "Node.js" "Service" {
                    facilitySyncJob = component "Facility Sync Job" "Daily Accela facility list sync" "Cron Job"
                    reminderScheduler = component "Reminder Scheduler" "24H and 1H appointment reminders" "Cron Job"
                    eligibilityRefresh = component "Eligibility Refresh" "Periodic eligibility status update" "Cron Job"
                    surveyTrigger = component "Survey Trigger" "7-day post-results survey nudge" "Cron Job"
                }
            }

            # --- Data Layer ---
            group "Data Layer" {
                patientDb = container "Patient Database" "Patient profiles, consents, survey responses" "PostgreSQL" "Database"

                providerDb = container "Provider Database" "Facilities, physicians, specialties" "PostgreSQL" "Database"

                appointmentDb = container "Appointment Database" "IFHAS appointments and booking history" "PostgreSQL" "Database"

                notificationQueue = container "Notification Queue" "Async notification processing" "Redis / RabbitMQ" "Queue"

                cacheLayer = container "Cache Layer" "API response caching and session store" "Redis" "Cache"
            }
        }

        # ==========================================
        # TAMM PORTAL (Government)
        # ==========================================

        tamm = softwareSystem "TAMM Portal" "Abu Dhabi government services portal - entry point for IFHAS" "External"

        # ==========================================
        # RELATIONSHIPS - System Context
        # ==========================================

        # Users to Systems
        citizen -> tamm "Accesses government services"
        citizen -> sahatna "Books IFHAS appointments, views results"
        citizen -> sahatna.mobileApp "Uses for IFHAS journey" "HTTPS"
        citizen -> sahatna.webPortal "Uses for IFHAS journey" "HTTPS"

        physician -> emrSystems "Records screening results"
        physician -> malaffi "Accesses patient questionnaire"

        dohAdmin -> strapiCms "Manages IFHAS content"
        dohAdmin -> accela "Manages facility licensing"

        dohDataTeam -> sahatna "Reviews survey analytics"

        facilityAdmin -> emrSystems "Manages appointments"

        # System to System
        tamm -> sahatna "Embeds IFHAS widget" "HTTPS"
        tamm -> sahatna.tammWidget "Displays IFHAS banner"

        sahatna -> daman "Checks eligibility, retrieves IFHAS history" "REST/HTTPS"
        sahatna -> malaffi "Retrieves screening results" "HL7/FHIR"
        sahatna -> accela "Syncs licensed IFHAS facilities" "REST/HTTPS"
        sahatna -> uaePass "Authenticates citizens" "OAuth 2.0"
        sahatna -> emrSystems "Books appointments, retrieves slots" "HL7/REST"
        sahatna -> firebase "Sends push notifications" "FCM"
        sahatna -> strapiCms "Fetches IFHAS content" "REST/HTTPS"

        emrSystems -> malaffi "Submits screening results" "HL7"

        # ==========================================
        # RELATIONSHIPS - Container Level
        # ==========================================

        # Presentation to Gateway
        sahatna.mobileApp -> sahatna.apiGateway "API calls" "HTTPS/JSON"
        sahatna.webPortal -> sahatna.apiGateway "API calls" "HTTPS/JSON"
        sahatna.tammWidget -> sahatna.apiGateway "Eligibility check" "HTTPS/JSON"

        # Gateway to Services
        sahatna.apiGateway -> sahatna.identityService "Auth requests" "gRPC"
        sahatna.apiGateway -> sahatna.patientService "Patient requests" "gRPC"
        sahatna.apiGateway -> sahatna.providerService "Provider requests" "gRPC"
        sahatna.apiGateway -> sahatna.appointmentService "Booking requests" "gRPC"
        sahatna.apiGateway -> sahatna.phrService "Results requests" "gRPC"
        sahatna.apiGateway -> sahatna.cmsService "Content requests" "gRPC"
        sahatna.apiGateway -> sahatna.integrationService "Eligibility requests" "gRPC"

        # Service to Service
        sahatna.appointmentService -> sahatna.integrationService "Eligibility, authorization" "gRPC"
        sahatna.appointmentService -> sahatna.providerService "Facility, physician lookup" "gRPC"
        sahatna.appointmentService -> sahatna.notificationService "Booking confirmations" "Async"

        sahatna.phrService -> sahatna.integrationService "Fetch results from Malaffi" "gRPC"

        sahatna.patientService -> sahatna.notificationService "Survey notifications" "Async"

        sahatna.batchService -> sahatna.integrationService "Sync jobs" "gRPC"
        sahatna.batchService -> sahatna.notificationService "Scheduled reminders" "Async"
        sahatna.batchService -> sahatna.providerService "Facility updates" "gRPC"

        sahatna.cmsService -> strapiCms "Fetch content" "REST"

        # Service to External
        sahatna.identityService -> uaePass "OAuth authentication" "OAuth 2.0"
        sahatna.integrationService -> daman "Member eligibility API" "REST"
        sahatna.integrationService -> malaffi "Health records API" "HL7/FHIR"
        sahatna.integrationService -> accela "Licensing API" "REST"
        sahatna.appointmentService -> emrSystems "Appointment API" "HL7/REST"
        sahatna.notificationService -> firebase "Push notifications" "FCM"

        # Service to Data
        sahatna.patientService -> sahatna.patientDb "Reads/writes" "SQL"
        sahatna.providerService -> sahatna.providerDb "Reads/writes" "SQL"
        sahatna.appointmentService -> sahatna.appointmentDb "Reads/writes" "SQL"
        sahatna.notificationService -> sahatna.notificationQueue "Enqueues messages" "AMQP"
        sahatna.identityService -> sahatna.cacheLayer "Session cache" "Redis Protocol"
        sahatna.apiGateway -> sahatna.cacheLayer "Response cache" "Redis Protocol"

        # ==========================================
        # RELATIONSHIPS - Component Level
        # ==========================================

        # Identity Service Components
        sahatna.identityService.authController -> sahatna.identityService.sessionManager "Creates sessions"
        sahatna.identityService.authController -> sahatna.identityService.uaePassAdapter "Delegates auth"
        sahatna.identityService.uaePassAdapter -> uaePass "OAuth flow"

        # Integration Service Components
        sahatna.integrationService.integrationOrchestrator -> sahatna.integrationService.damanAdapter "Eligibility checks"
        sahatna.integrationService.integrationOrchestrator -> sahatna.integrationService.malaffiAdapter "Results retrieval"
        sahatna.integrationService.integrationOrchestrator -> sahatna.integrationService.accelaAdapter "Facility sync"
        sahatna.integrationService.damanAdapter -> daman "API calls"
        sahatna.integrationService.malaffiAdapter -> malaffi "HL7/FHIR calls"
        sahatna.integrationService.accelaAdapter -> accela "API calls"

        # Appointment Service Components
        sahatna.appointmentService.bookingController -> sahatna.appointmentService.slotManager "Get available slots"
        sahatna.appointmentService.bookingController -> sahatna.appointmentService.emrGateway "Create appointment"
        sahatna.appointmentService.bookingController -> sahatna.appointmentService.appointmentTracker "Track status"
        sahatna.appointmentService.emrGateway -> emrSystems "EMR integration"

        # Notification Service Components
        sahatna.notificationService.nudgeEngine -> sahatna.notificationService.templateEngine "Generate message"
        sahatna.notificationService.nudgeEngine -> sahatna.notificationService.pushHandler "Send push"
        sahatna.notificationService.nudgeEngine -> sahatna.notificationService.smsHandler "Send SMS"
        sahatna.notificationService.nudgeEngine -> sahatna.notificationService.emailHandler "Send email"
        sahatna.notificationService.pushHandler -> firebase "FCM API"

        # Batch Service Components
        sahatna.batchService.facilitySyncJob -> sahatna.integrationService.accelaAdapter "Sync facilities"
        sahatna.batchService.reminderScheduler -> sahatna.notificationService.nudgeEngine "Trigger reminders"
        sahatna.batchService.surveyTrigger -> sahatna.notificationService.nudgeEngine "Trigger surveys"

        # ==========================================
        # DEPLOYMENT MODEL
        # ==========================================

        deploymentEnvironment "Production" {
            deploymentNode "Azure Region - UAE North" {
                deploymentNode "Azure Kubernetes Service" {
                    deploymentNode "App Namespace" {
                        containerInstance sahatna.apiGateway
                        containerInstance sahatna.identityService
                        containerInstance sahatna.patientService
                        containerInstance sahatna.providerService
                        containerInstance sahatna.appointmentService
                        containerInstance sahatna.integrationService
                        containerInstance sahatna.phrService
                        containerInstance sahatna.notificationService
                        containerInstance sahatna.cmsService
                        containerInstance sahatna.batchService
                    }
                }

                deploymentNode "Azure Database for PostgreSQL" {
                    containerInstance sahatna.patientDb
                    containerInstance sahatna.providerDb
                    containerInstance sahatna.appointmentDb
                }

                deploymentNode "Azure Cache for Redis" {
                    containerInstance sahatna.cacheLayer
                    containerInstance sahatna.notificationQueue
                }
            }

            deploymentNode "Mobile Devices" {
                deploymentNode "iOS" {
                    containerInstance sahatna.mobileApp
                }
                deploymentNode "Android" {
                    containerInstance sahatna.mobileApp
                }
            }

            deploymentNode "Web Browsers" {
                containerInstance sahatna.webPortal
                containerInstance sahatna.tammWidget
            }
        }
    }

    # ==========================================
    # VIEWS
    # ==========================================

    views {
        # System Context View
        systemContext sahatna "SystemContext" {
            include *
            autoLayout tb
            title "IFHAS System Context"
            description "Shows Sahatna IFHAS module in context with users and external systems"
        }

        # Container View
        container sahatna "Containers" {
            include *
            autoLayout tb
            title "IFHAS Container Diagram"
            description "Shows the containers/applications within Sahatna for IFHAS"
        }

        # Component View - Integration Service
        component sahatna.integrationService "IntegrationComponents" {
            include *
            autoLayout lr
            title "Integration Service Components"
            description "Shows adapters for external system integration"
        }

        # Component View - Appointment Service
        component sahatna.appointmentService "AppointmentComponents" {
            include *
            autoLayout lr
            title "Appointment Service Components"
            description "Shows booking and EMR integration components"
        }

        # Component View - Notification Service
        component sahatna.notificationService "NotificationComponents" {
            include *
            autoLayout lr
            title "Notification Service Components"
            description "Shows nudge engine and delivery channels"
        }

        # Component View - Identity Service
        component sahatna.identityService "IdentityComponents" {
            include *
            autoLayout lr
            title "Identity Service Components"
            description "Shows authentication and UAE Pass integration"
        }

        # Deployment View
        deployment sahatna "Production" "Deployment" {
            include *
            autoLayout tb
            title "IFHAS Production Deployment"
            description "Shows Azure cloud deployment architecture"
        }

        # Dynamic View - Booking Flow
        dynamic sahatna "BookingFlow" "IFHAS Appointment Booking Flow" {
            citizen -> sahatna.mobileApp "1. Open IFHAS landing page"
            sahatna.mobileApp -> sahatna.apiGateway "2. Request available packages"
            sahatna.apiGateway -> sahatna.integrationService "3. Check eligibility"
            sahatna.integrationService -> daman "4. GET member details & history"
            sahatna.apiGateway -> sahatna.providerService "5. Get IFHAS facilities"
            sahatna.providerService -> sahatna.providerDb "6. Query facility list"
            citizen -> sahatna.mobileApp "7. Select package & facility"
            sahatna.mobileApp -> sahatna.apiGateway "8. Get physicians for specialty"
            sahatna.apiGateway -> sahatna.providerService "9. Query physicians"
            citizen -> sahatna.mobileApp "10. Select physician & time slot"
            sahatna.mobileApp -> sahatna.apiGateway "11. Submit booking request"
            sahatna.apiGateway -> sahatna.appointmentService "12. Create appointment"
            sahatna.appointmentService -> sahatna.integrationService "13. Request authorization"
            sahatna.appointmentService -> emrSystems "14. POST appointment to EMR"
            sahatna.appointmentService -> sahatna.appointmentDb "15. Save booking"
            sahatna.appointmentService -> sahatna.notificationService "16. Trigger confirmation"
            sahatna.notificationService -> firebase "17. Send push notification"
            autoLayout lr
        }

        # Dynamic View - Results Flow
        dynamic sahatna "ResultsFlow" "IFHAS Results Retrieval Flow" {
            citizen -> sahatna.mobileApp "1. Open screening results"
            sahatna.mobileApp -> sahatna.apiGateway "2. GET IFHAS results"
            sahatna.apiGateway -> sahatna.phrService "3. Fetch results"
            sahatna.phrService -> sahatna.integrationService "4. Query health records"
            sahatna.integrationService -> malaffi "5. GET encounters with ICS filter"
            sahatna.integrationService -> malaffi "6. GET lab results by visit ID"
            autoLayout lr
        }

        # Styles
        styles {
            element "Person" {
                shape Person
                background #08427B
                color #ffffff
            }
            element "Citizen" {
                background #1168BD
            }
            element "Physician" {
                background #438DD5
            }
            element "Admin" {
                background #999999
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Target" {
                background #08427B
            }
            element "External" {
                background #999999
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Mobile" {
                shape MobileDevicePortrait
            }
            element "Web" {
                shape WebBrowser
            }
            element "Gateway" {
                shape Hexagon
            }
            element "Service" {
                shape RoundedBox
            }
            element "Database" {
                shape Cylinder
                background #438DD5
            }
            element "Queue" {
                shape Pipe
                background #85BBF0
            }
            element "Cache" {
                shape Ellipse
                background #85BBF0
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
        }

        theme default
    }

}

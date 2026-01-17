#!/bin/bash
#
# Test script for OpenCode agents (bash 3.2 compatible)
# Tests all plan-phase agents to verify they work within 32K context
#
# Usage:
#   ./scripts/test-agents.sh              # Run all tests
#   ./scripts/test-agents.sh ba-agent     # Test specific agent
#   ./scripts/test-agents.sh --quick      # Quick smoke test
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENCODE_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${OPENCODE_DIR}/test-output"
TIMEOUT_SECONDS=180
QUICK_MODE=false
SPECIFIC_AGENT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            TIMEOUT_SECONDS=90
            shift
            ;;
        *)
            SPECIFIC_AGENT="$1"
            shift
            ;;
    esac
done

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[FAIL]${NC} $1"; }

# Setup
setup() {
    log_info "Setting up test environment..."
    mkdir -p "$OUTPUT_DIR"
    cd "$OPENCODE_DIR"

    if ! command -v opencode &> /dev/null; then
        log_error "opencode command not found"
        exit 1
    fi

    log_info "Working directory: $OPENCODE_DIR"
}

# Run a single agent test
run_test() {
    local test_name="$1"
    local agent="$2"
    local prompt="$3"

    local output_file="${OUTPUT_DIR}/${test_name}-$(date +%Y%m%d-%H%M%S).md"

    log_info "Testing: $test_name"
    log_info "  Agent: $agent"
    log_info "  Prompt: ${prompt:0:80}..."

    local start_time=$(date +%s)

    # Build command - no --skill flag, skills loaded via agent instructions
    local cmd="opencode run --agent $agent"

    log_info "  Running: $cmd"

    # Execute (no timeout on mac without coreutils)
    local exit_code=0
    $cmd "$prompt" > "$output_file" 2>&1 || exit_code=$?

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    if [[ $exit_code -eq 0 ]]; then
        local output_size=$(wc -c < "$output_file" | tr -d ' ')

        if [[ $output_size -lt 100 ]]; then
            log_warning "$test_name: Minimal output ($output_size bytes)"
            cat "$output_file"
            return 1
        elif grep -qi "error.*context\|token limit\|exceeded" "$output_file"; then
            log_error "$test_name: Context limit issue detected"
            head -20 "$output_file"
            return 1
        else
            log_success "$test_name: Completed in ${duration}s (${output_size} bytes)"
            log_info "  Output: $output_file"
            # Show preview
            echo "  Preview: $(head -5 "$output_file" | tr '\n' ' ' | cut -c1-150)..."
            return 0
        fi
    else
        log_error "$test_name: Failed (exit code $exit_code)"
        head -30 "$output_file"
        return 1
    fi
}

# Main test runner
run_all_tests() {
    local total=0
    local passed=0
    local failed=0

    echo ""
    echo "=========================================="
    echo "  OpenCode Agent Test Suite"
    echo "  Mode: $([ "$QUICK_MODE" == true ] && echo "Quick" || echo "Full")"
    echo "=========================================="
    echo ""

    # Define tests: name|agent|prompt (no skill flag - skills auto-load)
    local tests=""

    if [[ "$QUICK_MODE" == true ]]; then
        tests="
ba-agent|ba-agent|Use the BRD skill. Problem statement: A healthcare clinic needs an online appointment booking system. Current state: 85% of appointments booked via phone with 8-minute average call time and 35% abandonment rate. Business objective: Reduce call volume by 40% through online self-scheduling. Generate a complete BRD with all sections.
qa-architect|qa-architect|Use the test-strategy skill. Create a test strategy for a patient appointment scheduling system with these features: search slots, book appointment, cancel appointment, send reminders. Include test pyramid ratios, coverage requirements, and sample test scenarios.
risk-analyst|risk-analyst|Use the risk-assessment skill. Assess risks for a patient appointment system that integrates with Epic EHR via FHIR APIs. Consider: API rate limits during peak hours, concurrent booking race conditions, SMS notification failures, and scope creep for telehealth features.
"
    else
        tests="
ba-agent|ba-agent|Use the BRD skill to generate a Business Requirements Document. Problem statement: A healthcare clinic needs an online appointment booking system. Current state: 85% of appointments booked via phone calls averaging 8 minutes each, with 2400 calls per day and 35% abandonment rate during peak hours. Stakeholders: Patients, Providers, Scheduling Staff, IT, Finance. Business objective: Enable patient self-scheduling to reduce call volume by 40%. Constraints: Must integrate with Epic EHR, HIPAA compliant, budget 250K. Generate the complete BRD with all 7 sections.
business-architect|business-architect|Use the archimate skill. Create an ArchiMate 3.1 business layer model for a patient appointment scheduling system. Include: BusinessActors (Patient, Provider, Scheduler), BusinessRoles (Appointment Requester, Schedule Manager), BusinessProcesses (Book Appointment, Manage Availability, Send Reminder), BusinessServices (Scheduling Service, Notification Service), BusinessObjects (Appointment, Time Slot, Patient Record). Generate valid Archi-compatible XML.
app-architect|app-architect|Use the archimate skill. Create an ArchiMate 3.1 application layer model for appointment scheduling. Include: ApplicationComponents (Scheduling Module, Provider Module, Notification Module), ApplicationServices (Slot Query Service, Booking Service, Reminder Service), ApplicationInterfaces (REST API, Admin UI), DataObjects (AppointmentDTO, SlotDTO, ProviderDTO). Show realization relationships to business layer. Generate valid Archi-compatible XML.
solution-architect-api|solution-architect|Use the openapi skill. Generate an OpenAPI 3.1 specification for an appointment scheduling API. Endpoints needed: GET /api/v1/slots (search by provider, date range, visit type), POST /api/v1/appointments (book with slotId, patientId, reason), GET /api/v1/appointments/{id}, DELETE /api/v1/appointments/{id} (cancel). Include schemas for Slot, Appointment, AppointmentCreate, Error. Add pagination, auth, and error responses.
solution-architect-sql|solution-architect|Use the sql-schema skill. Generate a PostgreSQL DDL schema for appointment scheduling. Tables needed: providers (id, name, specialty, email), provider_availability (provider_id, day_of_week, start_time, end_time), blocked_times (provider_id, start_datetime, end_datetime, reason), appointments (id, provider_id, patient_id, scheduled_start, status, confirmation_number). Include UUID primary keys, indexes, foreign keys, audit columns, and triggers for updated_at.
qa-architect|qa-architect|Use the test-strategy skill. Create a comprehensive test strategy for a patient appointment portal. Features to test: slot search, appointment booking, cancellation, reminders. Define: test pyramid with 70/20/10 split, coverage targets per component type (services 90%, controllers 80%, repos 75%), quality gates for PR and release. Include sample test scenarios with preconditions, test cases, and expected results for the booking feature.
risk-analyst|risk-analyst|Use the risk-assessment skill. Perform a risk assessment for a patient appointment scheduling system integrating with Epic EHR. Analyze: Technical risks (EHR API rate limits of 100 req/min during peak 200+ req/min, concurrent booking race conditions, notification delivery failures), Dependency risks (Epic FHIR API changes, third-party SMS provider), Scope risks (telehealth feature creep, unclear cancellation policy). Include risk matrix, scoring (L x I), mitigations, contingencies, and monitoring indicators.
"
    fi

    # Process each test
    echo "$tests" | while IFS='|' read -r name agent prompt; do
        # Skip empty lines
        [[ -z "$name" ]] && continue

        # Filter by specific agent if provided
        if [[ -n "$SPECIFIC_AGENT" ]] && [[ "$agent" != *"$SPECIFIC_AGENT"* ]]; then
            continue
        fi

        echo "----------------------------------------"
        total=$((total + 1))

        if run_test "$name" "$agent" "$prompt"; then
            passed=$((passed + 1))
        else
            failed=$((failed + 1))
        fi
        echo ""

        # Write counts to temp file for subshell
        echo "$total $passed $failed" > "${OUTPUT_DIR}/.counts"
    done

    # Read final counts
    if [[ -f "${OUTPUT_DIR}/.counts" ]]; then
        read total passed failed < "${OUTPUT_DIR}/.counts"
        rm -f "${OUTPUT_DIR}/.counts"
    fi

    echo "=========================================="
    echo "  Test Summary"
    echo "=========================================="
    echo "  Total:  $total"
    echo -e "  ${GREEN}Passed${NC}: $passed"
    echo -e "  ${RED}Failed${NC}: $failed"
    echo ""
    echo "  Output: $OUTPUT_DIR"
    echo "=========================================="

    [[ $failed -eq 0 ]]
}

# Run
setup
run_all_tests

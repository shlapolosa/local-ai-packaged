#!/bin/bash
#
# Full Pipeline Test - Tests ALL agents from the End-to-End Planning Pipeline
# Covers Phases 2 through 4.5 as defined in the plan
#
# Usage:
#   ./scripts/test-pipeline-full.sh           # Run all phases
#   ./scripts/test-pipeline-full.sh --phase 3 # Test specific phase
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENCODE_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${OPENCODE_DIR}/test-output/full-pipeline-$(date +%Y%m%d-%H%M%S)"
SPECIFIC_PHASE=""

# Healthcare problem statement (consistent across all tests)
PROBLEM_STATEMENT="A healthcare clinic needs an online appointment booking system. Current state: 85% of appointments booked via phone with 8-minute average call time and 35% abandonment rate. Business objective: Reduce call volume by 40% through online self-scheduling. Budget: 250K. Timeline: 8 months. Must integrate with Epic EHR via FHIR APIs. HIPAA compliance required."

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --phase)
            SPECIFIC_PHASE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[FAIL]${NC} $1"; }
log_phase() { echo -e "\n${CYAN}═══════════════════════════════════════════════════════════${NC}"; echo -e "${CYAN}  PHASE $1: $2${NC}"; echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}\n"; }

# Setup
setup() {
    log_info "Setting up full pipeline test..."
    mkdir -p "$OUTPUT_DIR"
    cd "$OPENCODE_DIR"
    log_info "Output directory: $OUTPUT_DIR"
    echo ""
}

# Run agent test
run_agent() {
    local phase="$1"
    local agent="$2"
    local skill="$3"
    local description="$4"
    local prompt="$5"
    local output_file="${OUTPUT_DIR}/phase${phase}-${agent}-${skill}.md"

    log_info "Testing: $agent ($skill) - $description"

    local start_time=$(date +%s)
    local exit_code=0

    opencode run --agent "$agent" "$prompt" > "$output_file" 2>&1 || exit_code=$?

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local output_size=$(wc -c < "$output_file" | tr -d ' ')

    if [[ $exit_code -eq 0 ]] && [[ $output_size -gt 500 ]]; then
        log_success "$agent: ${duration}s, ${output_size} bytes"
        return 0
    else
        log_error "$agent: Failed (exit: $exit_code, size: $output_size)"
        head -5 "$output_file" | sed 's/^/    /'
        return 1
    fi
}

# Phase 2: BRD Generation
test_phase_2() {
    log_phase "2" "BRD Generation"
    run_agent "2" "ba-agent" "brd" "Business Requirements Document" \
        "Generate a Business Requirements Document for: ${PROBLEM_STATEMENT}"
}

# Phase 3: TOGAF Architecture (all 6 architects)
test_phase_3() {
    log_phase "3" "TOGAF Architecture (6 agents)"

    # Business Architect
    run_agent "3" "business-architect" "archimate" "Business Layer Model" \
        "Using the archimate skill, create an ArchiMate 3.1 business layer model for patient appointment scheduling. Include: BusinessActors (Patient, Provider, Scheduler), BusinessProcesses (Book Appointment, Cancel Appointment, Send Reminder), BusinessServices (Scheduling Service, Notification Service). Context: ${PROBLEM_STATEMENT}"

    # Compliance Architect
    run_agent "3" "compliance" "archimate" "Compliance Model" \
        "Using the archimate skill, create an ArchiMate 3.1 model showing HIPAA compliance controls for patient appointment data. Include security aspects, data protection requirements, audit logging. Context: ${PROBLEM_STATEMENT}"

    # Data Architect
    run_agent "3" "data-architect" "archimate" "Data Layer Model" \
        "Using the archimate skill, create an ArchiMate 3.1 data layer model for appointment scheduling. Include: DataObjects (Patient, Provider, Appointment, TimeSlot), data flows between components. Context: ${PROBLEM_STATEMENT}"

    # Application Architect
    run_agent "3" "app-architect" "archimate" "Application Layer Model" \
        "Using the archimate skill, create an ArchiMate 3.1 application layer model. Include: ApplicationComponents (Scheduling API, Provider Portal, Patient Portal), ApplicationServices (Slot Query, Booking Service), ApplicationInterfaces (REST API, Web UI). Context: ${PROBLEM_STATEMENT}"

    # Security Architect
    run_agent "3" "security-architect" "archimate" "Security Model" \
        "Using the archimate skill, create an ArchiMate 3.1 security model for the appointment system. Include authentication, authorization, encryption at rest/transit, audit logging. Context: ${PROBLEM_STATEMENT}"

    # Infrastructure Architect
    run_agent "3" "infra-architect" "archimate" "Technology Layer Model" \
        "Using the archimate skill, create an ArchiMate 3.1 technology layer model. Include: cloud infrastructure, database servers, API gateway, load balancer, monitoring. Context: ${PROBLEM_STATEMENT}"
}

# Phase 3.5: Solution Design
test_phase_3_5() {
    log_phase "3.5" "Solution Design (OpenAPI + SQL)"

    # OpenAPI Specification
    run_agent "3.5" "solution-architect" "openapi" "OpenAPI Specification" \
        "Using the openapi skill, generate an OpenAPI 3.1 specification for appointment scheduling. Endpoints: GET /slots (search by provider, date), POST /appointments (book), GET /appointments/{id}, DELETE /appointments/{id} (cancel), POST /reminders. Include schemas for Slot, Appointment, Provider, Error. Context: ${PROBLEM_STATEMENT}"

    # SQL Schema
    run_agent "3.5" "solution-architect" "sql-schema" "SQL DDL Schema" \
        "Using the sql-schema skill, generate PostgreSQL DDL for appointment scheduling. Tables: providers (id, name, specialty, email), patients (id, name, email, phone), appointments (id, provider_id, patient_id, scheduled_time, status, created_at), time_slots (id, provider_id, start_time, end_time, available). Include indexes, foreign keys, and triggers. Context: ${PROBLEM_STATEMENT}"
}

# Phase 3.6: QA + Risk Assessment
test_phase_3_6() {
    log_phase "3.6" "QA Strategy + Risk Assessment"

    # QA Architect
    run_agent "3.6" "qa-architect" "test-strategy" "Test Strategy" \
        "Using the test-strategy skill, create a test strategy for patient appointment scheduling. Features: slot search, booking, cancellation, reminders. Define test pyramid (70/20/10), coverage targets, sample test scenarios for booking flow. Context: ${PROBLEM_STATEMENT}"

    # Risk Analyst
    run_agent "3.6" "risk-analyst" "risk-assessment" "Risk Assessment" \
        "Using the risk-assessment skill, assess risks for patient appointment system. Analyze: Technical risks (Epic API rate limits 100 req/min, concurrent booking races), Dependency risks (FHIR API changes, SMS provider), Scope risks (telehealth feature creep). Include risk matrix and mitigations. Context: ${PROBLEM_STATEMENT}"
}

# Phase 4: PRD Generation
test_phase_4() {
    log_phase "4" "PRD Generation"

    run_agent "4" "ba-agent" "prd" "Product Requirements Document" \
        "Using the prd skill, generate a Product Requirements Document in RPG format. The BRD established: online appointment booking to reduce call volume 40%. Features: slot search, booking, cancellation, automated reminders. Include all 9 sections with dependency syntax for Task Master parsing. Context: ${PROBLEM_STATEMENT}"
}

# Phase 4.5: Task Master (techlead) - SKIPPED for now
# Will be configured separately with local model in container
test_phase_4_5() {
    log_phase "4.5" "Task Master Planning (SKIPPED)"
    log_warning "Task Master will be configured separately - skipping for now"
    return 0
}

# Summary
print_summary() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  FULL PIPELINE TEST SUMMARY${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Output directory: $OUTPUT_DIR"
    echo ""
    echo "Generated artifacts:"
    ls -la "$OUTPUT_DIR"/*.md 2>/dev/null | awk '{print "  " $9 " (" $5 " bytes)"}' | sed "s|$OUTPUT_DIR/||" || echo "  No artifacts"
    echo ""

    # Count passes/fails
    local total=$(ls "$OUTPUT_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
    local large=$(ls -la "$OUTPUT_DIR"/*.md 2>/dev/null | awk '$5 > 500 {count++} END {print count+0}')
    echo "Results: $large/$total agents produced substantial output (>500 bytes)"
    echo ""
}

# Main
main() {
    setup
    local failed=0

    if [[ -z "$SPECIFIC_PHASE" ]] || [[ "$SPECIFIC_PHASE" == "2" ]]; then
        test_phase_2 || ((failed++))
    fi

    if [[ -z "$SPECIFIC_PHASE" ]] || [[ "$SPECIFIC_PHASE" == "3" ]]; then
        test_phase_3 || ((failed++))
    fi

    if [[ -z "$SPECIFIC_PHASE" ]] || [[ "$SPECIFIC_PHASE" == "3.5" ]]; then
        test_phase_3_5 || ((failed++))
    fi

    if [[ -z "$SPECIFIC_PHASE" ]] || [[ "$SPECIFIC_PHASE" == "3.6" ]]; then
        test_phase_3_6 || ((failed++))
    fi

    if [[ -z "$SPECIFIC_PHASE" ]] || [[ "$SPECIFIC_PHASE" == "4" ]]; then
        test_phase_4 || ((failed++))
    fi

    if [[ -z "$SPECIFIC_PHASE" ]] || [[ "$SPECIFIC_PHASE" == "4.5" ]]; then
        test_phase_4_5 || ((failed++))
    fi

    print_summary

    if [[ $failed -eq 0 ]]; then
        log_success "All pipeline phases completed!"
    else
        log_error "$failed phase(s) had failures"
    fi
}

main

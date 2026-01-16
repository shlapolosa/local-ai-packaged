#!/bin/bash
#
# Test script simulating the End-to-End Planning Pipeline call chain
# Tests agents in the order they'll be invoked by n8n workflow
#
# Usage:
#   ./scripts/test-pipeline.sh              # Run full pipeline test
#   ./scripts/test-pipeline.sh --phase 2    # Test specific phase
#   ./scripts/test-pipeline.sh --quick      # Quick smoke test (shorter prompts)
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
OUTPUT_DIR="${OPENCODE_DIR}/test-output/pipeline-$(date +%Y%m%d-%H%M%S)"
QUICK_MODE=false
SPECIFIC_PHASE=""
TIMEOUT_SECONDS=180

# Sample problem statement (used throughout pipeline)
PROBLEM_STATEMENT="A healthcare clinic needs an online appointment booking system. Current state: 85% of appointments booked via phone with 8-minute average call time and 35% abandonment rate. Business objective: Reduce call volume by 40% through online self-scheduling. Budget: 250K. Timeline: 8 months. Must integrate with Epic EHR via FHIR APIs. HIPAA compliance required."

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            TIMEOUT_SECONDS=120
            shift
            ;;
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
    log_info "Setting up pipeline test environment..."
    mkdir -p "$OUTPUT_DIR"
    cd "$OPENCODE_DIR"

    if ! command -v opencode &> /dev/null; then
        log_error "opencode command not found"
        exit 1
    fi

    log_info "Output directory: $OUTPUT_DIR"
    log_info "Mode: $([ "$QUICK_MODE" == true ] && echo "Quick" || echo "Full")"
    echo ""
}

# Run a single agent test
run_agent() {
    local phase="$1"
    local agent="$2"
    local skill="$3"
    local prompt="$4"
    local output_file="${OUTPUT_DIR}/phase${phase}-${agent}-${skill}.md"

    log_info "Agent: $agent | Skill: $skill"

    local start_time=$(date +%s)
    local exit_code=0

    opencode run --agent "$agent" "$prompt" > "$output_file" 2>&1 || exit_code=$?

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local output_size=$(wc -c < "$output_file" | tr -d ' ')

    if [[ $exit_code -eq 0 ]] && [[ $output_size -gt 500 ]]; then
        log_success "Completed in ${duration}s (${output_size} bytes)"
        # Check if correct skill was used
        if grep -q "skills_${skill}" "$output_file" 2>/dev/null || grep -q "# Business Requirements\|# Product Requirements\|ArchiMate\|openapi:\|CREATE TABLE\|Test Strategy\|Risk Assessment" "$output_file"; then
            log_success "Output appears to use correct skill format"
        else
            log_warning "Could not verify skill usage in output"
        fi
        echo "  Output: $output_file"
        echo "  Preview: $(head -3 "$output_file" | tr '\n' ' ' | cut -c1-100)..."
        return 0
    else
        log_error "Failed (exit: $exit_code, size: $output_size bytes)"
        if [[ -f "$output_file" ]]; then
            echo "  Error output:"
            head -10 "$output_file" | sed 's/^/    /'
        fi
        return 1
    fi
}

# Phase 2: BRD Generation
test_phase_2() {
    log_phase "2" "BRD Generation (ba-agent + brd skill)"

    local prompt="Generate a Business Requirements Document for: ${PROBLEM_STATEMENT}"
    run_agent "2" "ba-agent" "brd" "$prompt"
}

# Phase 3: Architecture (TOGAF agents with archimate skill)
test_phase_3() {
    log_phase "3" "Architecture Generation (archimate skill)"

    # Business Architect
    log_info "--- Business Architecture ---"
    local ba_prompt="Using the archimate skill, create an ArchiMate 3.1 business layer model for patient appointment scheduling. Include: BusinessActors (Patient, Provider, Scheduler), BusinessProcesses (Book Appointment, Cancel Appointment, Send Reminder), BusinessServices (Scheduling Service, Notification Service). Context: ${PROBLEM_STATEMENT}"
    run_agent "3" "business-architect" "archimate" "$ba_prompt"

    if [[ "$QUICK_MODE" == false ]]; then
        # Application Architect
        log_info "--- Application Architecture ---"
        local app_prompt="Using the archimate skill, create an ArchiMate 3.1 application layer model for appointment scheduling. Include: ApplicationComponents (Scheduling API, Provider Portal, Patient Portal), ApplicationServices (Slot Query, Booking Service), DataObjects (Appointment, TimeSlot, Provider). Context: ${PROBLEM_STATEMENT}"
        run_agent "3" "app-architect" "archimate" "$app_prompt"
    fi
}

# Phase 3.5: Solution Design (openapi + sql-schema skills)
test_phase_3_5() {
    log_phase "3.5" "Solution Design (openapi + sql-schema skills)"

    # OpenAPI
    log_info "--- OpenAPI Specification ---"
    local api_prompt="Using the openapi skill, generate an OpenAPI 3.1 specification for appointment scheduling. Endpoints: GET /slots (search by provider, date), POST /appointments (book), GET /appointments/{id}, DELETE /appointments/{id} (cancel). Include schemas for Slot, Appointment, Error. Context: ${PROBLEM_STATEMENT}"
    run_agent "3.5" "solution-architect" "openapi" "$api_prompt"

    if [[ "$QUICK_MODE" == false ]]; then
        # SQL Schema
        log_info "--- SQL Schema ---"
        local sql_prompt="Using the sql-schema skill, generate PostgreSQL DDL for appointment scheduling. Tables: providers (id, name, specialty), appointments (id, provider_id, patient_id, scheduled_time, status), time_slots (provider_id, start_time, end_time, available). Include indexes and foreign keys. Context: ${PROBLEM_STATEMENT}"
        run_agent "3.5" "solution-architect" "sql-schema" "$sql_prompt"
    fi
}

# Phase 3.6: QA + Risk (parallel in real workflow)
test_phase_3_6() {
    log_phase "3.6" "QA Strategy + Risk Assessment"

    # QA Architect
    log_info "--- Test Strategy ---"
    local qa_prompt="Using the test-strategy skill, create a test strategy for patient appointment scheduling. Features: slot search, booking, cancellation, reminders. Define test pyramid (70/20/10), coverage targets, sample test scenarios. Context: ${PROBLEM_STATEMENT}"
    run_agent "3.6" "qa-architect" "test-strategy" "$qa_prompt"

    if [[ "$QUICK_MODE" == false ]]; then
        # Risk Analyst
        log_info "--- Risk Assessment ---"
        local risk_prompt="Using the risk-assessment skill, assess risks for patient appointment system. Analyze: Technical risks (Epic API rate limits, concurrent booking races), Dependency risks (FHIR API changes, SMS provider), Scope risks (telehealth creep). Include risk matrix and mitigations. Context: ${PROBLEM_STATEMENT}"
        run_agent "3.6" "risk-analyst" "risk-assessment" "$risk_prompt"
    fi
}

# Phase 4: PRD Generation
test_phase_4() {
    log_phase "4" "PRD Generation (ba-agent + prd skill)"

    local prompt="Using the prd skill, generate a Product Requirements Document in RPG format for Task Master. Include all 9 sections with dependency syntax. The BRD established: online appointment booking to reduce call volume 40%. Features needed: slot search, booking, cancellation, reminders. Context: ${PROBLEM_STATEMENT}"
    run_agent "4" "ba-agent" "prd" "$prompt"
}

# Summary
print_summary() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  PIPELINE TEST SUMMARY${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Output directory: $OUTPUT_DIR"
    echo ""
    echo "Generated artifacts:"
    ls -la "$OUTPUT_DIR"/*.md 2>/dev/null | awk '{print "  " $NF " (" $5 " bytes)"}' || echo "  No artifacts generated"
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

    print_summary

    if [[ $failed -eq 0 ]]; then
        log_success "All pipeline tests passed!"
        return 0
    else
        log_error "$failed phase(s) had failures"
        return 1
    fi
}

main

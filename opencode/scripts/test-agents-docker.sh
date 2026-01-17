#!/bin/bash
#
# Docker-compatible test script for OpenCode agents
# Run this on the host server to test agents inside the opencode container
#
# Usage:
#   ./scripts/test-agents-docker.sh              # Run all tests
#   ./scripts/test-agents-docker.sh ba-agent     # Test specific agent
#   ./scripts/test-agents-docker.sh --quick      # Quick smoke test
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CONTAINER_NAME="opencode"
TIMEOUT_SECONDS=180
QUICK_MODE=false

# Test cases: "agent:skill:prompt"
declare -a TEST_CASES=(
    "ba-agent:brd:Generate a BRD for online appointment booking to reduce call center volume by 40%"
    "business-architect:archimate:Create ArchiMate business model for patient scheduling with actors and processes"
    "app-architect:archimate:Create ArchiMate application model for scheduling with components and services"
    "solution-architect:openapi:Generate OpenAPI spec for appointment booking API with slots and appointments"
    "solution-architect:sql-schema:Generate PostgreSQL schema for appointments with providers and availability"
    "qa-architect:test-strategy:Create test strategy with pyramid ratios and coverage for scheduling system"
    "risk-analyst:risk-assessment:Assess technical and dependency risks for EHR-integrated scheduling"
)

declare -a QUICK_CASES=(
    "ba-agent:brd:BRD for appointment booking"
    "qa-architect:test-strategy:Test strategy for scheduling"
    "risk-analyst:risk-assessment:Risk assessment for scheduling"
)

# Parse args
SPECIFIC_AGENT=""
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

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_error() { echo -e "${RED}[FAIL]${NC} $1"; }

# Check container
check_container() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        log_error "Container '$CONTAINER_NAME' is not running"
        log_info "Start it with: docker start $CONTAINER_NAME"
        exit 1
    fi
    log_info "Container '$CONTAINER_NAME' is running"
}

run_test() {
    local agent="$1"
    local skill="$2"
    local prompt="$3"

    log_info "Testing: $agent --skill $skill"
    log_info "  Prompt: ${prompt:0:60}..."

    local start_time=$(date +%s)

    # Run inside container
    local cmd="opencode run --agent $agent --skill $skill \"$prompt\""
    local output

    if output=$(timeout "$TIMEOUT_SECONDS" docker exec "$CONTAINER_NAME" bash -c "$cmd" 2>&1); then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        local output_len=${#output}

        if [[ $output_len -lt 100 ]]; then
            log_error "$agent: Minimal output ($output_len chars)"
            echo "Output: $output"
            return 1
        elif echo "$output" | grep -qi "error.*context\|token limit\|exceeded"; then
            log_error "$agent: Context limit exceeded"
            return 1
        else
            log_success "$agent: Completed in ${duration}s ($output_len chars)"
            # Show first 200 chars of output
            echo "  Preview: ${output:0:200}..."
            return 0
        fi
    else
        local exit_code=$?
        if [[ $exit_code -eq 124 ]]; then
            log_error "$agent: Timeout after ${TIMEOUT_SECONDS}s"
        else
            log_error "$agent: Failed (exit $exit_code)"
            echo "Output: $output"
        fi
        return 1
    fi
}

main() {
    check_container

    local cases
    if [[ "$QUICK_MODE" == true ]]; then
        cases=("${QUICK_CASES[@]}")
    else
        cases=("${TEST_CASES[@]}")
    fi

    local total=0
    local passed=0
    local failed=0

    echo ""
    echo "=========================================="
    echo "  OpenCode Agent Tests (Docker)"
    echo "  Mode: $([ "$QUICK_MODE" == true ] && echo "Quick" || echo "Full")"
    echo "=========================================="
    echo ""

    for case_str in "${cases[@]}"; do
        IFS=':' read -r agent skill prompt <<< "$case_str"

        # Filter by specific agent if provided
        if [[ -n "$SPECIFIC_AGENT" ]] && [[ "$agent" != "$SPECIFIC_AGENT"* ]]; then
            continue
        fi

        total=$((total + 1))
        echo "----------------------------------------"

        if run_test "$agent" "$skill" "$prompt"; then
            passed=$((passed + 1))
        else
            failed=$((failed + 1))
        fi
        echo ""
    done

    echo "=========================================="
    echo "  Results: $passed/$total passed"
    if [[ $failed -gt 0 ]]; then
        echo -e "  ${RED}$failed failed${NC}"
    fi
    echo "=========================================="

    [[ $failed -eq 0 ]]
}

main

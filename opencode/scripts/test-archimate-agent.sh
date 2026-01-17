#!/bin/bash
# test-archimate-agent.sh - Test ArchiMate generation with JSON → XML transformation

set -e

OUTPUT_DIR="${1:-test-output/archimate-$(date +%Y%m%d-%H%M%S)}"
OPENCODE_HOST="${OPENCODE_HOST:-localhost}"
OPENCODE_PORT="${OPENCODE_PORT:-22}"

# Problem statement for testing
PROBLEM_STATEMENT="A healthcare clinic needs an online appointment booking system. Current state: 85% of appointments booked via phone with 8-minute average call time and 35% abandonment rate. Business objective: Reduce call volume by 40% through online self-scheduling. Must integrate with Epic EHR via FHIR APIs. HIPAA compliance required."

mkdir -p "$OUTPUT_DIR"

# Test colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to test a single agent
test_agent() {
    local agent_name="$1"
    local layer_name="$2"
    local output_prefix="$3"

    log_info "Testing agent: $agent_name ($layer_name)"

    local json_file="$OUTPUT_DIR/${output_prefix}.json"
    local xml_file="$OUTPUT_DIR/${output_prefix}.archimate"

    # Run agent and capture JSON output
    log_info "Running agent via Docker..."

    docker exec opencode opencode run --agent "$agent_name" \
        "Using the archimate skill, create an ArchiMate 3.1 model for the $layer_name of this project: $PROBLEM_STATEMENT" \
        > "$json_file" 2>&1 || {
            log_error "Agent execution failed"
            return 1
        }

    # Check if output starts with { (valid JSON)
    local first_char=$(head -c 1 "$json_file")
    if [ "$first_char" != "{" ]; then
        log_warn "Output does not start with '{'. First 200 chars:"
        head -c 200 "$json_file"
        echo ""

        # Try to extract JSON from output (in case there's preamble)
        log_info "Attempting to extract JSON..."
        grep -o '{.*}' "$json_file" | head -1 > "${json_file}.extracted" 2>/dev/null || true

        if [ -s "${json_file}.extracted" ]; then
            mv "${json_file}.extracted" "$json_file"
            log_info "Extracted JSON"
        else
            log_error "Could not extract valid JSON"
            rm -f "${json_file}.extracted"
            return 1
        fi
    fi

    # Validate JSON
    if ! python3 -c "import json; json.load(open('$json_file'))" 2>/dev/null; then
        log_error "Invalid JSON in $json_file"
        return 1
    fi

    log_info "Valid JSON output received"

    # Transform to ArchiMate XML
    log_info "Transforming JSON to ArchiMate XML..."

    if python3 scripts/json-to-archimate.py "$json_file" "$xml_file" 2>&1; then
        log_info "Successfully created $xml_file"

        # Validate XML structure
        if grep -q 'archimate:model' "$xml_file"; then
            log_info "XML contains valid ArchiMate structure"

            # Count elements
            local elem_count=$(grep -c 'xsi:type="archimate:' "$xml_file" || echo "0")
            log_info "Element count: $elem_count"

            return 0
        else
            log_error "XML missing ArchiMate structure"
            return 1
        fi
    else
        log_error "Transformation failed"
        return 1
    fi
}

# Main test sequence
log_info "========================================="
log_info "ArchiMate Agent Test Suite"
log_info "Output directory: $OUTPUT_DIR"
log_info "========================================="

# Test results
PASSED=0
FAILED=0

# Test Business Architect
if test_agent "business-architect" "business layer (actors, processes, services, objects)" "business-layer"; then
    ((PASSED++))
else
    ((FAILED++))
fi

echo ""

# Test Application Architect
if test_agent "app-architect" "application layer (components, services, interfaces, data objects)" "application-layer"; then
    ((PASSED++))
else
    ((FAILED++))
fi

echo ""

# Test Infrastructure Architect
if test_agent "infra-architect" "technology layer (nodes, devices, system software, networks)" "technology-layer"; then
    ((PASSED++))
else
    ((FAILED++))
fi

echo ""

# Test Data Architect
if test_agent "data-architect" "data architecture (data objects, flows, access relationships)" "data-layer"; then
    ((PASSED++))
else
    ((FAILED++))
fi

echo ""

# Test Security Architect
if test_agent "security-architect" "security architecture (constraints, requirements, security controls)" "security-layer"; then
    ((PASSED++))
else
    ((FAILED++))
fi

echo ""

# Test Compliance Architect
if test_agent "compliance" "compliance architecture (constraints, requirements, principles for HIPAA)" "compliance-layer"; then
    ((PASSED++))
else
    ((FAILED++))
fi

echo ""

# Summary
log_info "========================================="
log_info "Test Summary"
log_info "========================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

# List generated files
log_info "Generated files:"
ls -la "$OUTPUT_DIR"/*.archimate 2>/dev/null || echo "No ArchiMate files generated"
ls -la "$OUTPUT_DIR"/*.json 2>/dev/null || echo "No JSON files"

if [ $FAILED -gt 0 ]; then
    exit 1
fi

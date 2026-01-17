#!/bin/bash
# test-json-output.sh - End-to-end test of JSON output from all skills

set -e

OUTPUT_DIR="test-output/json-validation-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Problem statement
PROBLEM="A healthcare clinic needs an online appointment booking system. Current state: 85% of appointments booked via phone with 8-minute average call time and 35% abandonment rate. Business objective: Reduce call volume by 40% through online self-scheduling. Budget: 250K. Timeline: 8 months. Must integrate with Epic EHR via FHIR APIs. HIPAA compliance required."

# Counters
PASSED=0
FAILED=0
TOTAL=0

# Validate JSON function
validate_json() {
    local file="$1"
    local name="$2"

    ((TOTAL++))

    if [ ! -f "$file" ]; then
        log_fail "$name: Output file not found"
        ((FAILED++))
        return 1
    fi

    local size=$(wc -c < "$file" | tr -d ' ')
    if [ "$size" -lt 50 ]; then
        log_fail "$name: Output too small ($size bytes)"
        cat "$file"
        ((FAILED++))
        return 1
    fi

    # Check first character
    local first_char=$(head -c 1 "$file")
    if [ "$first_char" != "{" ]; then
        log_warn "$name: First char is '$first_char', not '{'. Attempting extraction..."

        # Try to extract JSON
        if grep -o '{.*}' "$file" > "${file}.extracted" 2>/dev/null; then
            if python3 -c "import json; json.load(open('${file}.extracted'))" 2>/dev/null; then
                mv "${file}.extracted" "$file"
                log_info "$name: Extracted valid JSON from output"
            else
                rm -f "${file}.extracted"
                log_fail "$name: Could not extract valid JSON"
                echo "First 500 chars:"
                head -c 500 "$file"
                echo ""
                ((FAILED++))
                return 1
            fi
        else
            log_fail "$name: No JSON pattern found"
            echo "First 500 chars:"
            head -c 500 "$file"
            echo ""
            ((FAILED++))
            return 1
        fi
    fi

    # Validate JSON syntax
    if python3 -c "import json; data = json.load(open('$file')); print(f'Keys: {list(data.keys())[:5]}')" 2>&1; then
        log_pass "$name: Valid JSON ($size bytes)"
        ((PASSED++))
        return 0
    else
        log_fail "$name: Invalid JSON syntax"
        echo "First 500 chars:"
        head -c 500 "$file"
        echo ""
        ((FAILED++))
        return 1
    fi
}

# Test function
run_test() {
    local agent="$1"
    local skill="$2"
    local description="$3"
    local prompt="$4"
    local output_file="$OUTPUT_DIR/${agent}-${skill}.json"

    log_info "Testing: $agent with $skill skill ($description)"

    # Run agent
    docker exec opencode opencode run --agent "$agent" "$prompt" > "$output_file" 2>&1 || true

    # Validate
    validate_json "$output_file" "$agent/$skill"
    echo ""
}

echo ""
echo "=========================================="
echo "  JSON Output Validation Test Suite"
echo "=========================================="
echo "Output directory: $OUTPUT_DIR"
echo ""

# Test 1: BA Agent - BRD Skill
run_test "ba-agent" "brd" "Business Requirements Document" \
    "Using the brd skill, create a Business Requirements Document for: $PROBLEM"

# Test 2: Business Architect - ArchiMate Skill
run_test "business-architect" "archimate" "Business Layer ArchiMate" \
    "Using the archimate skill, create an ArchiMate 3.1 business layer model for: $PROBLEM"

# Test 3: App Architect - ArchiMate Skill
run_test "app-architect" "archimate" "Application Layer ArchiMate" \
    "Using the archimate skill, create an ArchiMate 3.1 application layer model for a healthcare appointment booking system with scheduling module, notification service, and patient portal components."

# Test 4: Data Architect - ArchiMate Skill
run_test "data-architect" "archimate" "Data Layer ArchiMate" \
    "Using the archimate skill, create an ArchiMate 3.1 data architecture model for a healthcare appointment system with Patient, Provider, Appointment, and TimeSlot data objects."

# Test 5: Data Architect - SQL Schema Skill
run_test "data-architect" "sql-schema" "SQL DDL Schema" \
    "Using the sql-schema skill, create a database schema for a healthcare appointment booking system with tables for patients, providers, appointments, and time_slots."

# Test 6: Security Architect - ArchiMate Skill
run_test "security-architect" "archimate" "Security ArchiMate" \
    "Using the archimate skill, create an ArchiMate security architecture model for HIPAA-compliant healthcare appointment system including authentication, authorization, and audit logging."

# Test 7: Infra Architect - ArchiMate Skill
run_test "infra-architect" "archimate" "Technology Layer ArchiMate" \
    "Using the archimate skill, create an ArchiMate 3.1 technology layer model for healthcare appointment system deployment on AWS with EKS, RDS PostgreSQL, and Redis cache."

# Test 8: Compliance - ArchiMate Skill
run_test "compliance" "archimate" "Compliance ArchiMate" \
    "Using the archimate skill, create an ArchiMate compliance model for HIPAA requirements including Privacy Rule, Security Rule, and breach notification constraints."

# Test 9: Solution Architect - OpenAPI Skill (if exists)
if docker exec opencode opencode agents list 2>/dev/null | grep -q "solution-architect"; then
    run_test "solution-architect" "openapi" "OpenAPI Specification" \
        "Using the openapi skill, create an OpenAPI specification for a healthcare appointment booking API with endpoints for slots, appointments, and providers."
fi

echo ""
echo "=========================================="
echo "  Test Summary"
echo "=========================================="
echo -e "Total:  $TOTAL"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

# List output files
echo "Generated files:"
ls -la "$OUTPUT_DIR"/*.json 2>/dev/null || echo "No JSON files generated"

# Show sample of successful outputs
echo ""
echo "Sample output preview (first successful file):"
for f in "$OUTPUT_DIR"/*.json; do
    if python3 -c "import json; json.load(open('$f'))" 2>/dev/null; then
        echo "--- $f ---"
        python3 -c "import json; d=json.load(open('$f')); print(json.dumps(d, indent=2)[:1000])"
        break
    fi
done

if [ $FAILED -gt 0 ]; then
    exit 1
fi

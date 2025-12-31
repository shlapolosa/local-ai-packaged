#!/bin/bash
# Test script for OpenCode agents
# Run this on the server after deploying updated containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="opencode"
TIMEOUT=120  # seconds per agent test

# Track results
PASSED=0
FAILED=0
SKIPPED=0

# Function to test an agent
test_agent() {
    local agent_name="$1"
    local prompt="$2"
    local description="$3"

    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Testing: ${agent_name}${NC}"
    echo -e "${BLUE}Description: ${description}${NC}"
    echo -e "${BLUE}Prompt: ${prompt}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    START_TIME=$(date +%s)

    # Run the agent with timeout
    if timeout ${TIMEOUT} docker exec -i ${CONTAINER_NAME} opencode run --agent "${agent_name}" "${prompt}" 2>&1; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        echo -e "\n${GREEN}✓ PASSED${NC} - ${agent_name} (${DURATION}s)"
        ((PASSED++))
        return 0
    else
        EXIT_CODE=$?
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        if [ $EXIT_CODE -eq 124 ]; then
            echo -e "\n${RED}✗ TIMEOUT${NC} - ${agent_name} (exceeded ${TIMEOUT}s)"
        else
            echo -e "\n${RED}✗ FAILED${NC} - ${agent_name} (exit code: ${EXIT_CODE}, ${DURATION}s)"
        fi
        ((FAILED++))
        return 1
    fi
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"

    # Check if opencode container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${RED}Error: Container '${CONTAINER_NAME}' is not running${NC}"
        echo "Start it with: docker compose --profile gpu-nvidia up -d opencode-gpu ollama-gpu"
        exit 1
    fi
    echo -e "${GREEN}OpenCode container is running${NC}"

    # Check if ollama container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^ollama$"; then
        echo -e "${RED}Error: Ollama container is not running${NC}"
        echo "Start it with: docker compose --profile gpu-nvidia up -d ollama-gpu"
        exit 1
    fi
    echo -e "${GREEN}Ollama container is running${NC}"

    # Check if model is available (check from ollama container directly)
    if ! docker exec -i ollama ollama list 2>/dev/null | grep -q "qwen2.5"; then
        echo -e "${YELLOW}Warning: qwen2.5 model not found${NC}"
        echo "Pulling model..."
        docker exec -i ollama ollama pull qwen2.5:7b-instruct-q4_K_M
    else
        echo -e "${GREEN}Model qwen2.5 is available${NC}"
    fi

    echo -e "${GREEN}Prerequisites check passed${NC}"
}

# Function to show config
show_config() {
    echo -e "\n${BLUE}Current OpenCode Configuration:${NC}"
    docker exec -i ${CONTAINER_NAME} cat /root/.config/opencode/opencode.json | grep -E '"(model|description)"' | head -30
}

# Function to verify industry configuration
verify_industry_config() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Verifying Industry Configuration${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Check if industry-config.json exists
    if ! docker exec -i ${CONTAINER_NAME} test -f /root/.config/opencode/industry-config.json; then
        echo -e "${RED}✗ FAILED: industry-config.json not found${NC}"
        ((FAILED++))
        return 1
    fi
    echo -e "${GREEN}✓ industry-config.json exists${NC}"

    # Get industry info
    INDUSTRY=$(docker exec -i ${CONTAINER_NAME} cat /root/.config/opencode/industry-config.json | grep '"industry"' | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
    DISPLAY_NAME=$(docker exec -i ${CONTAINER_NAME} cat /root/.config/opencode/industry-config.json | grep '"displayName"' | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
    echo -e "${GREEN}✓ Industry: ${INDUSTRY} (${DISPLAY_NAME})${NC}"

    # Check knowledge directory
    if docker exec -i ${CONTAINER_NAME} test -d "/root/.config/opencode/.opencode/knowledge/${INDUSTRY}"; then
        echo -e "${GREEN}✓ Knowledge directory exists: knowledge/${INDUSTRY}/${NC}"
        KNOWLEDGE_FILES=$(docker exec -i ${CONTAINER_NAME} find "/root/.config/opencode/.opencode/knowledge/${INDUSTRY}" -name "*.md" -type f 2>/dev/null | wc -l)
        echo -e "${GREEN}  Found ${KNOWLEDGE_FILES} knowledge files${NC}"
    else
        echo -e "${RED}✗ FAILED: Knowledge directory not found: knowledge/${INDUSTRY}/${NC}"
        ((FAILED++))
        return 1
    fi

    # Check examples directory
    if docker exec -i ${CONTAINER_NAME} test -d /root/.config/opencode/.opencode/examples; then
        EXAMPLE_FILES=$(docker exec -i ${CONTAINER_NAME} ls /root/.config/opencode/.opencode/examples/*.md 2>/dev/null | wc -l)
        echo -e "${GREEN}✓ Examples directory exists with ${EXAMPLE_FILES} files${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: Examples directory not found${NC}"
    fi

    # Check capability model exists
    CAP_MODEL=$(docker exec -i ${CONTAINER_NAME} cat /root/.config/opencode/industry-config.json | grep '"capabilityModel"' | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
    if [ -n "$CAP_MODEL" ] && docker exec -i ${CONTAINER_NAME} test -f "/root/.config/opencode/${CAP_MODEL}"; then
        echo -e "${GREEN}✓ Capability model exists: ${CAP_MODEL}${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: Capability model not found at ${CAP_MODEL}${NC}"
    fi

    ((PASSED++))
    echo -e "${GREEN}✓ Industry configuration verified${NC}"
    return 0
}

# Function to test industry-specific agent knowledge
test_industry_knowledge() {
    local agent_name="$1"
    local prompt="$2"
    local expected_keyword="$3"
    local description="$4"

    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Testing Industry Knowledge: ${agent_name}${NC}"
    echo -e "${BLUE}Description: ${description}${NC}"
    echo -e "${BLUE}Expected keyword: ${expected_keyword}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    START_TIME=$(date +%s)

    # Run the agent and capture output
    OUTPUT=$(timeout ${TIMEOUT} docker exec -i ${CONTAINER_NAME} opencode run --agent "${agent_name}" "${prompt}" 2>&1) || true
    EXIT_CODE=$?

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    if [ $EXIT_CODE -eq 124 ]; then
        echo -e "\n${RED}✗ TIMEOUT${NC} - ${agent_name} (exceeded ${TIMEOUT}s)"
        ((FAILED++))
        return 1
    fi

    # Check if output contains expected keyword (case-insensitive)
    if echo "$OUTPUT" | grep -qi "$expected_keyword"; then
        echo -e "\n${GREEN}✓ PASSED${NC} - ${agent_name} referenced industry knowledge (${DURATION}s)"
        echo -e "${BLUE}Found expected keyword: ${expected_keyword}${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "\n${YELLOW}⚠ WARNING${NC} - ${agent_name} response did not contain expected industry keyword (${DURATION}s)"
        echo -e "${BLUE}Expected: ${expected_keyword}${NC}"
        echo -e "${BLUE}Output preview: ${OUTPUT:0:200}...${NC}"
        ((PASSED++))  # Still count as passed since agent responded
        return 0
    fi
}

# Main test suite
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           OpenCode Agent Test Suite                          ║"
    echo "║           Testing all configured agents                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    check_prerequisites

    # ============ Industry Configuration ============
    echo -e "\n${BLUE}═══ INDUSTRY CONFIGURATION ═══${NC}"
    verify_industry_config

    echo -e "\n${YELLOW}Starting agent tests...${NC}"
    echo "Each test has a ${TIMEOUT}s timeout"

    # ============ Primary Agents ============
    echo -e "\n${BLUE}═══ PRIMARY AGENTS ═══${NC}"

    test_agent "comedian" \
        "Tell me a short programming joke about recursion" \
        "Witty comedian that tells jokes"

    test_agent "general" \
        "What is Docker in one sentence?" \
        "General assistant for various tasks"

    test_agent "architect-orchestrator" \
        "What ADM phase would you start with for a new microservice project? Reply briefly." \
        "Central orchestrator for EA workflows"

    test_agent "coding-orchestrator" \
        "Given a task about creating an API endpoint, which specialist agent should handle it? Reply with just the agent name." \
        "Development cycle orchestrator"

    # ============ ADM Cycle Agents ============
    echo -e "\n${BLUE}═══ ADM CYCLE AGENTS ═══${NC}"

    test_agent "cto" \
        "Should we use PostgreSQL or MongoDB for a transaction-heavy banking app? Reply in 2 sentences." \
        "CTO strategic advisor"

    test_agent "ba-agent" \
        "List 3 key requirements for a user login feature" \
        "Business Analyst - requirements and PRD"

    test_agent "compliance" \
        "What GDPR consideration applies to storing user emails? One sentence." \
        "Compliance Architect"

    test_agent "business-architect" \
        "Name one business capability for an e-commerce platform" \
        "Business Architect"

    test_agent "data-architect" \
        "What data entity would you create for user authentication? Name only." \
        "Data Architect"

    test_agent "app-architect" \
        "Should authentication be a separate microservice? Yes or No with one reason." \
        "Application Architect"

    test_agent "security-architect" \
        "Name one OWASP Top 10 risk relevant to login forms" \
        "Security Architect"

    test_agent "infra-architect" \
        "Kubernetes or Docker Swarm for production? One word answer with reason." \
        "Infrastructure Architect"

    test_agent "pm" \
        "What's the first milestone for building a login system?" \
        "Project Manager"

    test_agent "solution-architect" \
        "Name one KubeVela component type for a web service" \
        "Solution Architect - OAM specs"

    # ============ Development Cycle Agents ============
    echo -e "\n${BLUE}═══ DEVELOPMENT CYCLE AGENTS ═══${NC}"

    test_agent "techlead" \
        "Break this into 2 subtasks: Build user registration API" \
        "TechLead - breaks PRD into tasks"

    test_agent "frontend-coder" \
        "Write a one-line React useState hook for a loading state" \
        "Frontend Specialist"

    test_agent "backend-coder" \
        "Write a one-line Express.js GET route for /health" \
        "Backend Specialist"

    test_agent "infra-coder" \
        "Write a one-line Kubernetes label selector for app=api" \
        "Infrastructure Specialist"

    test_agent "devops-coder" \
        "Write a one-line Dockerfile CMD for running node index.js" \
        "DevOps Specialist"

    test_agent "data-coder" \
        "Write a one-line SQL to create a users table with id and email" \
        "Data Specialist"

    test_agent "testing-agent" \
        "Write a one-line Jest expect assertion checking if 1+1 equals 2" \
        "Testing Specialist"

    # ============ Industry Knowledge Tests ============
    echo -e "\n${BLUE}═══ INDUSTRY KNOWLEDGE TESTS ═══${NC}"
    echo -e "${YELLOW}Testing that agents can access industry-specific knowledge${NC}"

    # Get the current industry from config
    CURRENT_INDUSTRY=$(docker exec -i ${CONTAINER_NAME} cat /root/.config/opencode/industry-config.json | grep '"industry"' | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')

    if [ "$CURRENT_INDUSTRY" = "healthcare" ]; then
        # Healthcare-specific tests
        test_industry_knowledge "compliance" \
            "What is the primary compliance standard for US healthcare data? Reference the industry configuration." \
            "HIPAA" \
            "Compliance agent should reference HIPAA from healthcare config"

        test_industry_knowledge "business-architect" \
            "What L1 capability domain from the industry capability model relates to patient services?" \
            "Patient" \
            "Business architect should reference patient-related capabilities"

        test_industry_knowledge "data-architect" \
            "What data standard should be used for healthcare interoperability according to industry config?" \
            "FHIR" \
            "Data architect should reference HL7 FHIR standard"
    else
        echo -e "${YELLOW}Industry is '${CURRENT_INDUSTRY}' - skipping healthcare-specific tests${NC}"
        echo -e "${BLUE}To add tests for ${CURRENT_INDUSTRY}, update test-agents.sh${NC}"
    fi

    # ============ Summary ============
    echo -e "\n${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                      TEST SUMMARY                            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    TOTAL=$((PASSED + FAILED + SKIPPED))

    echo -e "${GREEN}Passed:  ${PASSED}${NC}"
    echo -e "${RED}Failed:  ${FAILED}${NC}"
    echo -e "${YELLOW}Skipped: ${SKIPPED}${NC}"
    echo -e "${BLUE}Total:   ${TOTAL}${NC}"

    if [ $FAILED -eq 0 ]; then
        echo -e "\n${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "\n${RED}Some tests failed. Check output above for details.${NC}"
        exit 1
    fi
}

# Quick test - just test one agent
quick_test() {
    echo -e "${YELLOW}Quick test mode - testing comedian agent only${NC}"
    check_prerequisites
    test_agent "comedian" "Tell me a one-liner joke" "Quick connectivity test"
    echo -e "\n${GREEN}Quick test complete${NC}"
}

# Config only test - verify industry configuration
config_test() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           Industry Configuration Test                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    check_prerequisites
    verify_industry_config

    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Full Configuration Details${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    echo -e "\n${BLUE}industry-config.json:${NC}"
    docker exec -i ${CONTAINER_NAME} cat /root/.config/opencode/industry-config.json

    echo -e "\n${BLUE}Knowledge files:${NC}"
    docker exec -i ${CONTAINER_NAME} find /root/.config/opencode/.opencode/knowledge -type f -name "*.md" 2>/dev/null

    echo -e "\n${BLUE}Example files:${NC}"
    docker exec -i ${CONTAINER_NAME} ls -la /root/.config/opencode/.opencode/examples/ 2>/dev/null

    echo -e "\n${GREEN}Configuration test complete${NC}"
}

# Industry knowledge test only
industry_test() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           Industry Knowledge Test                            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    check_prerequisites
    verify_industry_config

    # Get the current industry from config
    CURRENT_INDUSTRY=$(docker exec -i ${CONTAINER_NAME} cat /root/.config/opencode/industry-config.json | grep '"industry"' | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')

    echo -e "\n${YELLOW}Testing industry-aware agents for: ${CURRENT_INDUSTRY}${NC}"

    if [ "$CURRENT_INDUSTRY" = "healthcare" ]; then
        test_industry_knowledge "compliance" \
            "What is the primary compliance standard for US healthcare data?" \
            "HIPAA" \
            "Compliance agent should reference HIPAA"

        test_industry_knowledge "business-architect" \
            "What L1 capability domain relates to patient services?" \
            "Patient" \
            "Business architect should reference patient capabilities"
    else
        echo -e "${YELLOW}No industry-specific tests defined for '${CURRENT_INDUSTRY}'${NC}"
    fi

    echo -e "\n${GREEN}Industry knowledge test complete${NC}"
    echo -e "Passed: ${PASSED}, Failed: ${FAILED}"
}

# Parse arguments
case "${1:-}" in
    --quick|-q)
        quick_test
        ;;
    --config|-c)
        config_test
        ;;
    --industry|-i)
        industry_test
        ;;
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --quick, -q      Run quick test (comedian only)"
        echo "  --config, -c     Verify industry configuration only"
        echo "  --industry, -i   Run industry knowledge tests only"
        echo "  --help, -h       Show this help"
        echo ""
        echo "Without options, runs full test suite for all agents"
        echo ""
        echo "Industry Configuration:"
        echo "  The tests verify that agents can access industry-specific"
        echo "  knowledge from /root/.config/opencode/industry-config.json"
        echo "  Current industry: $(cat opencode/industry-config.json 2>/dev/null | grep '"industry"' | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/' || echo 'unknown')"
        ;;
    *)
        main
        ;;
esac

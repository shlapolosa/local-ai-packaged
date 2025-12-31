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

    # Check if container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${RED}Error: Container '${CONTAINER_NAME}' is not running${NC}"
        echo "Start it with: docker compose --profile gpu-nvidia up -d opencode-gpu ollama-gpu"
        exit 1
    fi

    # Check if ollama is accessible
    if ! docker exec -i ${CONTAINER_NAME} curl -s http://ollama:11434/api/tags > /dev/null 2>&1; then
        echo -e "${RED}Error: Cannot reach Ollama from OpenCode container${NC}"
        echo "Check if Ollama container is running and healthy"
        exit 1
    fi

    # Check if model is available
    if ! docker exec -i ${CONTAINER_NAME} curl -s http://ollama:11434/api/tags | grep -q "qwen2.5"; then
        echo -e "${YELLOW}Warning: qwen2.5 model may not be loaded${NC}"
        echo "Pulling model..."
        docker exec -i ollama ollama pull qwen2.5:7b-instruct-q4_K_M
    fi

    echo -e "${GREEN}Prerequisites check passed${NC}"
}

# Function to show config
show_config() {
    echo -e "\n${BLUE}Current OpenCode Configuration:${NC}"
    docker exec -i ${CONTAINER_NAME} cat /root/.config/opencode/opencode.json | grep -E '"(model|description)"' | head -30
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

# Parse arguments
case "${1:-}" in
    --quick|-q)
        quick_test
        ;;
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --quick, -q    Run quick test (comedian only)"
        echo "  --help, -h     Show this help"
        echo ""
        echo "Without options, runs full test suite for all agents"
        ;;
    *)
        main
        ;;
esac

#!/bin/bash
# Deployment script for updating OpenCode agents on NVIDIA GPU server
# Run this after making changes to agent files or opencode.json

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROFILE="gpu-nvidia"
CONTAINER_NAME="opencode"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           OpenCode Agent Deployment Script                   ║"
echo "║           Profile: ${PROFILE}                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to check if we're in the right directory
check_directory() {
    if [ ! -f "docker-compose.yml" ]; then
        echo -e "${RED}Error: docker-compose.yml not found${NC}"
        echo "Please run this script from the local-ai-packaged directory"
        exit 1
    fi

    if [ ! -d "opencode" ]; then
        echo -e "${RED}Error: opencode directory not found${NC}"
        exit 1
    fi
}

# Step 1: Pull latest changes
pull_latest() {
    echo -e "\n${YELLOW}Step 1: Pulling latest changes from git...${NC}"

    if git pull; then
        echo -e "${GREEN}Git pull successful${NC}"
    else
        echo -e "${YELLOW}Warning: Git pull failed or no changes${NC}"
    fi
}

# Step 2: Show what changed in opencode directory
show_changes() {
    echo -e "\n${YELLOW}Step 2: Checking agent file changes...${NC}"

    echo -e "${BLUE}Agent files:${NC}"
    ls -la opencode/.opencode/agent/*.md 2>/dev/null || echo "No agent files found"

    echo -e "\n${BLUE}opencode.json last modified:${NC}"
    ls -la opencode/opencode.json 2>/dev/null || echo "opencode.json not found"
}

# Step 3: Stop and remove existing opencode container
stop_container() {
    echo -e "\n${YELLOW}Step 3: Stopping existing opencode container...${NC}"

    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true
        echo -e "${GREEN}Container stopped and removed${NC}"
    else
        echo -e "${BLUE}Container not running${NC}"
    fi
}

# Step 4: Rebuild opencode container
rebuild_container() {
    echo -e "\n${YELLOW}Step 4: Rebuilding opencode container...${NC}"

    docker compose --profile ${PROFILE} build opencode-gpu --no-cache
    echo -e "${GREEN}Container rebuilt${NC}"
}

# Step 5: Start containers
start_containers() {
    echo -e "\n${YELLOW}Step 5: Starting containers with profile ${PROFILE}...${NC}"

    docker compose --profile ${PROFILE} up -d opencode-gpu ollama-gpu
    echo -e "${GREEN}Containers started${NC}"
}

# Step 6: Wait for containers to be ready
wait_ready() {
    echo -e "\n${YELLOW}Step 6: Waiting for containers to be ready...${NC}"

    echo "Waiting for Ollama..."
    for i in {1..30}; do
        if docker exec -i ${CONTAINER_NAME} curl -s http://ollama:11434/api/tags > /dev/null 2>&1; then
            echo -e "${GREEN}Ollama is ready${NC}"
            break
        fi
        sleep 2
        echo -n "."
    done
}

# Step 7: Verify agent configuration
verify_agents() {
    echo -e "\n${YELLOW}Step 7: Verifying agent configuration...${NC}"

    echo -e "${BLUE}Configured agents in container:${NC}"
    docker exec -i ${CONTAINER_NAME} cat /root/.config/opencode/opencode.json | grep -E '"[a-z-]+":.*\{' | head -30

    echo -e "\n${BLUE}Agent instruction files in container:${NC}"
    docker exec -i ${CONTAINER_NAME} ls -la /root/.config/opencode/.opencode/agent/ 2>/dev/null || echo "Agent directory not found in config"
}

# Step 8: Quick test
quick_test() {
    echo -e "\n${YELLOW}Step 8: Running quick connectivity test...${NC}"
    echo "Note: First request may take 30-60s as model loads into VRAM"

    # First, verify Ollama connectivity
    echo -e "${BLUE}Testing Ollama API...${NC}"
    if docker exec -i ${CONTAINER_NAME} curl -s http://ollama:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}Ollama API reachable${NC}"
    else
        echo -e "${RED}Cannot reach Ollama API${NC}"
        return 1
    fi

    # Check if model exists
    echo -e "${BLUE}Checking model availability...${NC}"
    if docker exec -i ollama ollama list 2>/dev/null | grep -q "qwen2.5"; then
        echo -e "${GREEN}Model found${NC}"
    else
        echo -e "${YELLOW}Model not found, pulling...${NC}"
        docker exec -i ollama ollama pull qwen2.5:7b-instruct-q4_K_M
    fi

    # Run actual test with longer timeout (model loading can take time)
    echo -e "${BLUE}Running OpenCode agent test (timeout: 180s)...${NC}"
    if timeout 180 docker exec -i ${CONTAINER_NAME} opencode run --agent "general" "Reply with just: OK" 2>&1; then
        echo -e "\n${GREEN}Quick test passed!${NC}"
    else
        EXIT_CODE=$?
        echo -e "\n${RED}Quick test failed (exit code: ${EXIT_CODE})${NC}"
        if [ $EXIT_CODE -eq 124 ]; then
            echo "Timed out - model may still be loading or there's a connectivity issue"
        fi
        echo "Debug commands:"
        echo "  docker logs opencode --tail 50"
        echo "  docker logs ollama --tail 50"
        echo "  docker exec -it ollama ollama list"
    fi
}

# Main execution
main() {
    check_directory

    case "${1:-}" in
        --pull-only)
            pull_latest
            show_changes
            ;;
        --rebuild-only)
            stop_container
            rebuild_container
            start_containers
            wait_ready
            ;;
        --test-only)
            quick_test
            ;;
        --no-test)
            pull_latest
            show_changes
            stop_container
            rebuild_container
            start_containers
            wait_ready
            verify_agents
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  (no args)       Full deployment: pull, rebuild, start, test"
            echo "  --pull-only     Only pull latest changes"
            echo "  --rebuild-only  Only rebuild and restart containers"
            echo "  --test-only     Only run quick test"
            echo "  --no-test       Full deployment without quick test"
            echo "  --help, -h      Show this help"
            ;;
        *)
            pull_latest
            show_changes
            stop_container
            rebuild_container
            start_containers
            wait_ready
            verify_agents
            quick_test
            ;;
    esac

    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Deployment complete!${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

    echo -e "\n${YELLOW}Next steps:${NC}"
    echo "  1. Run full agent tests:  ./test-agents.sh"
    echo "  2. Run quick test only:   ./test-agents.sh --quick"
    echo "  3. Check container logs:  docker logs opencode"
    echo "  4. Interactive shell:     docker exec -it opencode /bin/sh"
}

main "$@"

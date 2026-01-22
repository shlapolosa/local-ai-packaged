#!/bin/bash
# Deployment script for updating OpenCode agents on NVIDIA GPU server
# Proxy-safe version: NO root access required

set -e

# =========================
# Proxy configuration
# =========================
PROXY_URL="http://proxy.internal.adhie.ae:8080"
USE_PROXY=false

# =========================
# Colors for output
# =========================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROFILE="gpu-nvidia"
CONTAINER_NAME="opencode"

# =========================
# Banner
# =========================
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           OpenCode Agent Deployment Script                   ║"
echo "║           Profile: ${PROFILE}                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# =========================
# Proxy helpers (NO ROOT)
# =========================
enable_proxy() {
    echo -e "${YELLOW}Using proxy via environment only:${NC} ${PROXY_URL}"

    export http_proxy="${PROXY_URL}"
    export https_proxy="${PROXY_URL}"
    export HTTP_PROXY="${PROXY_URL}"
    export HTTPS_PROXY="${PROXY_URL}"

    # Avoid proxying internal traffic
    export no_proxy="localhost,127.0.0.1,ollama"
    export NO_PROXY="localhost,127.0.0.1,ollama"
}

disable_proxy() {
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY no_proxy NO_PROXY
}

trap disable_proxy EXIT

# =========================
# Argument parsing
# =========================
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --use-proxy)
            USE_PROXY=true
            shift
            ;;
        --no-proxy)
            USE_PROXY=false
            shift
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

set -- "${POSITIONAL_ARGS[@]}"

if [ "${USE_PROXY}" = true ]; then
    enable_proxy
else
    echo -e "${BLUE}Running without proxy${NC}"
fi

# =========================
# Functions
# =========================
check_directory() {
    if [ ! -f "docker-compose.yml" ]; then
        echo -e "${RED}Error: docker-compose.yml not found${NC}"
        exit 1
    fi

    if [ ! -d "opencode" ]; then
        echo -e "${RED}Error: opencode directory not found${NC}"
        exit 1
    fi
}

pull_latest() {
    echo -e "\n${YELLOW}Step 1: Pulling latest changes from git...${NC}"
    git pull || echo -e "${YELLOW}Warning: Git pull failed or no changes${NC}"
}

show_changes() {
    echo -e "\n${YELLOW}Step 2: Checking agent file changes...${NC}"
    ls -la opencode/.opencode/agent/*.md 2>/dev/null || echo "No agent files found"
    ls -la opencode/opencode.json 2>/dev/null || echo "opencode.json not found"
}

stop_container() {
    echo -e "\n${YELLOW}Stopping existing opencode container...${NC}"
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
}

stop_all_containers() {
    docker stop opencode ollama 2>/dev/null || true
    docker rm opencode ollama 2>/dev/null || true
}

clean_opencode_rebuild() {
    echo -e "\n${YELLOW}Cleaning OpenCode images...${NC}"
    docker compose -p localai -f docker-compose.yml --profile ${PROFILE} down || true
    docker rmi $(docker images | grep opencode | awk '{print $3}') -f 2>/dev/null || true
}

rebuild_container() {
    echo -e "\n${YELLOW}Rebuilding OpenCode container...${NC}"

    BUILD_PROXY_ARGS=""
    if [ "${USE_PROXY}" = true ]; then
        BUILD_PROXY_ARGS="--build-arg http_proxy=${PROXY_URL} --build-arg https_proxy=${PROXY_URL}"
    fi

    docker compose --profile ${PROFILE} build opencode-gpu \
        --no-cache \
        ${BUILD_PROXY_ARGS}

    echo -e "${GREEN}Container rebuilt${NC}"
}

start_containers() {
    echo -e "\n${YELLOW}Starting containers...${NC}"
    docker compose --profile ${PROFILE} up -d opencode-gpu ollama-gpu
}

wait_ready() {
    echo -e "\n${YELLOW}Waiting for Ollama to be ready...${NC}"

    for i in {1..30}; do
        if docker exec -i ${CONTAINER_NAME} curl -s http://ollama:11434/api/tags >/dev/null 2>&1; then
            echo -e "${GREEN}Ollama is ready${NC}"
            return
        fi
        sleep 2
        echo -n "."
    done

    echo -e "${RED}Ollama did not become ready in time${NC}"
}

verify_agents() {
    echo -e "\n${YELLOW}Verifying agent configuration...${NC}"
    docker exec -i ${CONTAINER_NAME} ls -la /root/.config/opencode/.opencode/agent/ || true
}

quick_test() {
    echo -e "\n${YELLOW}Running quick connectivity test...${NC}"

    if timeout 180 docker exec -i ${CONTAINER_NAME} opencode run --agent "general" "Reply with just: OK"; then
        echo -e "${GREEN}Quick test passed${NC}"
    else
        echo -e "${RED}Quick test failed${NC}"
        echo "Debug:"
        echo "  docker logs opencode --tail 50"
        echo "  docker logs ollama --tail 50"
    fi
}

# =========================
# Main
# =========================
main() {
    check_directory

    case "${1:-}" in
        --pull-only)
            pull_latest
            show_changes
            ;;
        --build-only)
            pull_latest
            clean_opencode_rebuild
            rebuild_container
            ;;
        --rebuild-only)
            stop_container
            rebuild_container
            start_containers
            wait_ready
            verify_agents
            stop_all_containers
            ;;
        --test-only)
            quick_test
            ;;
        --no-test)
            pull_latest
            stop_container
            rebuild_container
            start_containers
            wait_ready
            verify_agents
            stop_all_containers
            ;;
        --keep-running)
            pull_latest
            stop_container
            rebuild_container
            start_containers
            wait_ready
            verify_agents
            quick_test
            echo -e "${YELLOW}Containers left running${NC}"
            ;;
        --help|-h)
            echo "Usage: $0 [options] [--use-proxy]"
            echo ""
            echo "Proxy options:"
            echo "  --use-proxy     Enable HTTP proxy (${PROXY_URL})"
            echo "  --no-proxy      Disable proxy (default)"
            echo ""
            echo "Deployment options:"
            echo "  --pull-only"
            echo "  --build-only"
            echo "  --rebuild-only"
            echo "  --test-only"
            echo "  --no-test"
            echo "  --keep-running"
            ;;
        *)
            pull_latest
            stop_container
            rebuild_container
            start_containers
            wait_ready
            verify_agents
            quick_test
            stop_all_containers
            ;;
    esac

    echo -e "\n${GREEN}Deployment complete!${NC}"
}

main "$@"

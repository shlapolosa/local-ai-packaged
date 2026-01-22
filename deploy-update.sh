#!/bin/bash
# Deployment script for updating OpenCode agents on NVIDIA GPU server
# Supports optional APT + environment proxy via CLI flag

set -e

# =========================
# Proxy configuration
# =========================
PROXY_URL="http://proxy.internal.adhie.ae:8080"
APT_PROXY_FILE="/etc/apt/apt.conf.d/99company-proxy"
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
# Proxy helpers
# =========================
enable_proxy() {
    echo -e "${YELLOW}Enabling proxy: ${PROXY_URL}${NC}"

    export http_proxy="${PROXY_URL}"
    export https_proxy="${PROXY_URL}"
    export HTTP_PROXY="${PROXY_URL}"
    export HTTPS_PROXY="${PROXY_URL}"

    if [ "$(id -u)" -ne 0 ]; then
        echo -e "${RED}Error: --use-proxy requires root (APT config)${NC}"
        exit 1
    fi

    cat <<EOF > "${APT_PROXY_FILE}"
Acquire::http::Proxy "${PROXY_URL}";
Acquire::https::Proxy "${PROXY_URL}";
EOF

    echo -e "${GREEN}APT proxy configured${NC}"
}

disable_proxy() {
    if [ -f "${APT_PROXY_FILE}" ]; then
        echo -e "${YELLOW}Removing APT proxy configuration${NC}"
        rm -f "${APT_PROXY_FILE}"
    fi

    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
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
# Functions (unchanged logic)
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
    ls -la opencode/.opencode/agent/*.md 2>/dev/null || true
    ls -la opencode/opencode.json 2>/dev/null || true
}

stop_container() {
    echo -e "\n${YELLOW}Stopping existing container...${NC}"
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
}

clean_opencode_rebuild() {
    docker compose -p localai -f docker-compose.yml --profile ${PROFILE} down || true
    docker rmi $(docker images | grep opencode | awk '{print $3}') -f 2>/dev/null || true
}

rebuild_container() {
    echo -e "\n${YELLOW}Rebuilding container...${NC}"
    docker compose --profile ${PROFILE} build opencode-gpu --no-cache
}

start_containers() {
    docker compose --profile ${PROFILE} up -d opencode-gpu ollama-gpu
}

wait_ready() {
    echo -e "\n${YELLOW}Waiting for Ollama...${NC}"
    for i in {1..30}; do
        docker exec ${CONTAINER_NAME} curl -s http://ollama:11434/api/tags && break
        sleep 2
    done
}

quick_test() {
    echo -e "\n${YELLOW}Running quick test...${NC}"
    docker exec -i ${CONTAINER_NAME} opencode run --agent "general" "Reply with just: OK"
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
        --test-only)
            quick_test
            ;;
        --help|-h)
            echo "Usage: $0 [options] [--use-proxy]"
            echo ""
            echo "Proxy options:"
            echo "  --use-proxy     Enable APT + env proxy (${PROXY_URL})"
            echo "  --no-proxy      Disable proxy (default)"
            echo ""
            echo "Deployment options:"
            echo "  --pull-only"
            echo "  --build-only"
            echo "  --test-only"
            ;;
        *)
            pull_latest
            stop_container
            rebuild_container
            start_containers
            wait_ready
            quick_test
            ;;
    esac

    echo -e "\n${GREEN}Deployment complete${NC}"
}

main "$@"

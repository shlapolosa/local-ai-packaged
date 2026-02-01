# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a self-hosted AI package that combines multiple AI and low-code development tools into a unified Docker Compose stack. The project provides a complete local AI development environment with LLMs (via Ollama), workflow automation (n8n), chat interfaces (Open WebUI), agent builders (Flowise), vector stores (Qdrant, Supabase), knowledge graphs (Neo4j), observability (Langfuse), and search (SearXNG).

## Architecture

### Multi-Stack Docker Compose Design

The project uses a unified Docker Compose project named `localai` that combines two separate compose files:

1. **Supabase Stack** (`supabase/docker/docker-compose.yml`): Cloned from the official Supabase repository during setup
2. **Local AI Stack** (`docker-compose.yml`): Main services including n8n, Ollama, Open WebUI, Flowise, etc.

Both stacks share the same Docker network and project name to enable seamless inter-service communication.

### Service Dependencies

- **n8n** depends on Postgres (from Supabase) for workflow storage and credential management
- **Open WebUI** connects to Ollama for LLM inference
- **Flowise** can use both Ollama and n8n for agent workflows
- **Langfuse** uses its own Postgres, ClickHouse, Redis, and MinIO for observability
- **Caddy** acts as a reverse proxy for all services, providing HTTPS via Let's Encrypt in production

### Network Architecture

All services communicate via internal Docker network. External access is routed through Caddy, which provides:
- Local development: localhost with different ports (`:8001` for n8n, `:8002` for Open WebUI, etc.)
- Production: Custom domains with automatic HTTPS (configured via `N8N_HOSTNAME`, `WEBUI_HOSTNAME`, etc. in `.env`)

### GPU Profile System

The project supports multiple GPU configurations via Docker Compose profiles:
- `cpu`: CPU-only Ollama
- `gpu-nvidia`: NVIDIA GPU support
- `gpu-amd`: AMD GPU support (ROCm)
- `none`: No Ollama container (use locally installed Ollama)

## Development Commands

### Starting the Stack

```bash
# Basic startup (CPU only)
python start_services.py --profile cpu

# With NVIDIA GPU
python start_services.py --profile gpu-nvidia

# With AMD GPU
python start_services.py --profile gpu-amd

# For production deployment (closes all ports except 80/443)
python start_services.py --profile gpu-nvidia --environment public

# For Mac users running Ollama locally (outside Docker)
python start_services.py --profile none
```

### Managing Services

```bash
# Stop all services
docker compose -p localai -f docker-compose.yml --profile <your-profile> down

# View logs for a specific service
docker compose -p localai logs -f <service-name>

# Restart a specific service
docker compose -p localai restart <service-name>

# Pull latest container versions
docker compose -p localai -f docker-compose.yml --profile <your-profile> pull
```

### Upgrading

```bash
# Stop all services
docker compose -p localai -f docker-compose.yml --profile <your-profile> down

# Pull latest versions
docker compose -p localai -f docker-compose.yml --profile <your-profile> pull

# Restart with updated containers
python start_services.py --profile <your-profile>
```

## Configuration

### Environment Variables

All configuration is managed through a single `.env` file in the root directory (created from `.env.example`).

**Critical secrets that must be set:**
- `N8N_ENCRYPTION_KEY`, `N8N_USER_MANAGEMENT_JWT_SECRET`: Generate with `openssl rand -hex 32`
- `POSTGRES_PASSWORD`: Shared by Supabase and n8n
- `JWT_SECRET`, `ANON_KEY`, `SERVICE_ROLE_KEY`: Supabase authentication keys
- `NEO4J_AUTH`: Format is `username/password`
- `CLICKHOUSE_PASSWORD`, `MINIO_ROOT_PASSWORD`, `LANGFUSE_SALT`, `NEXTAUTH_SECRET`, `ENCRYPTION_KEY`: Langfuse observability stack

**Production-only variables (for Caddy):**
- `N8N_HOSTNAME`, `WEBUI_HOSTNAME`, `FLOWISE_HOSTNAME`, etc.: Custom domains
- `LETSENCRYPT_EMAIL`: Email for Let's Encrypt certificates

### Service URLs (Local Development)

- n8n: http://localhost:5678
- Open WebUI: http://localhost:3000
- Flowise: http://localhost:3001
- Supabase Studio: http://localhost:8005
- Langfuse: http://localhost:3002
- Neo4j Browser: http://localhost:7474
- Ollama API: http://localhost:11434

### Inter-Service Communication

Services communicate using internal Docker hostnames:
- Ollama: `http://ollama:11434`
- Postgres (Supabase): `db` (host), port `5432`
- Qdrant: `http://qdrant:6333`
- Neo4j: `neo4j:7687` (Bolt), `neo4j:7474` (HTTP)
- SearXNG: `http://searxng:8080`

## Key Files and Directories

### Configuration Files

- `docker-compose.yml`: Main service definitions with GPU profiles
- `docker-compose.override.private.yml`: Private deployment (exposes all ports)
- `docker-compose.override.public.yml`: Public deployment (only ports 80/443)
- `Caddyfile`: Reverse proxy configuration
- `start_services.py`: Unified startup script that orchestrates both stacks

### Data Persistence

- `n8n/backup/`: Pre-configured n8n workflows and credentials
- `shared/`: Mounted to `/data/shared` in n8n container for file access
- `supabase/docker/volumes/`: Supabase data (created after first run)
- Docker volumes: `n8n_storage`, `ollama_storage`, `qdrant_storage`, `open-webui`, `flowise`, etc.

### Workflow Integration

- `n8n_pipe.py`: Open WebUI pipe function that enables chat interface to call n8n workflows
- `Local_RAG_AI_Agent_n8n_Workflow.json`: Pre-built RAG agent workflow
- `n8n-tool-workflows/`: Example n8n workflows for tools (Slack, Google Docs, Postgres)
- `flowise/`: Flowise chatflows and custom tool definitions

## Startup Sequence

The `start_services.py` script orchestrates the following:

1. Clone/update Supabase repository (sparse checkout of `docker/` directory only)
2. Copy root `.env` to `supabase/docker/.env`
3. Generate SearXNG secret key if not already configured
4. Handle SearXNG first-run permissions (temporarily removes `cap_drop: - ALL`)
5. Stop any existing containers from the `localai` project
6. Start Supabase stack first
7. Wait 10 seconds for Supabase initialization
8. Start local AI services stack
9. Pull Ollama models (`qwen2.5:7b-instruct-q4_K_M`, `nomic-embed-text`)

## Common Development Patterns

### Adding n8n Credentials

1. Access n8n at http://localhost:5678/home/credentials
2. For Ollama: Use `http://ollama:11434` as base URL
3. For Postgres (via Supabase): Host is `db`, use credentials from `.env`
4. For Qdrant: Use `http://qdrant:6333`

### Connecting Open WebUI to n8n

1. Create n8n workflow with webhook trigger, note the production URL
2. In Open WebUI, go to Workspace → Functions → Add Function
3. Paste contents of `n8n_pipe.py`
4. Configure `n8n_url` valve to the webhook URL
5. Toggle function on to enable in chat interface

### Mac Users Running Local Ollama

If running Ollama outside Docker on Mac:

1. Start services with `--profile none`
2. Update n8n container environment to use `OLLAMA_HOST=host.docker.internal:11434`
3. Update n8n Ollama credentials to use `http://host.docker.internal:11434/`

### Cloudflare Tunnel Setup (Production)

The README includes complete instructions for setting up Cloudflare Tunnel for exposing services on vast.ai or other cloud providers. The tunnel configuration routes all services through a single tunnel with separate subdomains.

## Troubleshooting Considerations

### Supabase Issues

- **Pooler restarting**: Check GitHub issue #30210 on supabase/supabase
- **Analytics fails after password change**: Delete `supabase/docker/volumes/db/data`
- **Connection issues**: Avoid `@` symbol in `POSTGRES_PASSWORD`
- **Missing files in supabase/**: Delete `supabase/` folder and re-run `start_services.py`

### SearXNG Permissions

If SearXNG container restarts continuously, run `chmod 755 searxng` to fix permissions.

### GPU Support

- **Windows**: Requires WSL 2 backend enabled in Docker Desktop
- **NVIDIA**: Follow Ollama Docker GPU instructions
- **AMD**: Linux only, requires ROCm drivers

### Docker Desktop Configuration

Ensure "Expose daemon on tcp://localhost:2375 without TLS" is enabled in Docker settings for Supabase analytics.

## ArchiMate Modeling

- **Default format**: ArchiMate Exchange File (.xml) - compatible with both ADOIT and Archi
- Schema: `http://www.opengroup.org/xsd/archimate/3.0/`

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md

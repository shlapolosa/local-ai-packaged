FROM ghcr.io/sst/opencode:latest

# Set working directory for the workspace
WORKDIR /workspace

# Create config directory
RUN mkdir -p /root/.config/opencode

# Copy the configuration files
COPY opencode.json /root/.config/opencode/opencode.json

# Copy industry configuration (configures industry-specific knowledge)
COPY industry-config.json /root/.config/opencode/industry-config.json
COPY industry-config.schema.json /root/.config/opencode/industry-config.schema.json

# Copy AGENTS.md (referenced in instructions array)
COPY AGENTS.md /root/.config/opencode/AGENTS.md

# Copy entire .opencode directory (agents, skills, knowledge, examples with nested structure)
COPY .opencode/ /root/.config/opencode/.opencode/

# Keep container running and allow exec into it
ENTRYPOINT ["tail", "-f", "/dev/null"]

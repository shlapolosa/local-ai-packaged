FROM ghcr.io/sst/opencode:latest

# Set working directory for the workspace
WORKDIR /workspace

# Create config directory
RUN mkdir -p /root/.config/opencode

# Copy the configuration file
COPY opencode.json /root/.config/opencode/opencode.json

# Copy AGENTS.md (referenced in instructions array)
COPY AGENTS.md /root/.config/opencode/AGENTS.md

# Copy entire .opencode directory (agents + skills with nested structure)
COPY .opencode/ /root/.config/opencode/.opencode/

# Keep container running and allow exec into it
ENTRYPOINT ["tail", "-f", "/dev/null"]

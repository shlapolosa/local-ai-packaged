FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install essential tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    ca-certificates \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Install OpenCode via official installer
RUN curl -fsSL https://opencode.ai/install | bash

# Add opencode to PATH
ENV PATH="/root/.local/bin:${PATH}"

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

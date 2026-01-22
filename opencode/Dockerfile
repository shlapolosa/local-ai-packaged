FROM ubuntu:22.04


ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV NO_PROXY=${NO_PROXY}


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

# Create symlink to /usr/bin (always in docker exec PATH)
RUN ln -sf /root/.opencode/bin/opencode /usr/bin/opencode && \
    opencode --version

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

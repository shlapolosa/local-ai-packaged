FROM ghcr.io/sst/opencode:latest

# Set working directory for the workspace
WORKDIR /workspace

# Create config directory
RUN mkdir -p /root/.config/opencode

# Copy the configuration file
COPY opencode.json /root/.config/opencode/opencode.json

# Keep container running and allow exec into it
ENTRYPOINT ["tail", "-f", "/dev/null"]

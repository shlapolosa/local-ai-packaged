FROM n8nio/n8n:latest

USER root
# n8nio/n8n:latest is now a Docker Hardened Alpine image with no package manager
# (apk is removed for security), so `apk add docker-cli` fails with "apk: not found".
# Copy the static docker CLI binary from the official docker image instead — distro/PM-agnostic.
COPY --from=docker:cli /usr/local/bin/docker /usr/local/bin/docker
USER node

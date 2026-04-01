# Copilot Agent Docker Environment
# Uses the GitHub Copilot CLI for agent execution

FROM python:3.11-slim

# Build-time proxy args (optional)
ARG http_proxy
ARG https_proxy
ARG no_proxy=localhost,127.0.0.1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    ca-certificates \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22.x (same as host, needed for copilot import.meta.resolve)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub Copilot CLI npm wrapper
RUN npm install -g @github/copilot@0.0.406

# Overwrite native binary with host's self-updated version (supports claude-opus-4.6)
COPY copilot-binary /usr/lib/node_modules/@github/copilot/node_modules/@github/copilot-linux-x64/copilot
RUN chmod +x /usr/lib/node_modules/@github/copilot/node_modules/@github/copilot-linux-x64/copilot

# Create non-root user
RUN useradd -m -s /bin/bash agent && \
    mkdir -p /workspace /home/agent/.config /agent_logs && \
    chown -R agent:agent /workspace /home/agent /agent_logs

WORKDIR /workspace

# Install Python dependencies
RUN pip install --no-cache-dir pyyaml

# Copy runner script
COPY --chown=agent:agent run_agent.sh /usr/local/bin/run_agent.sh
COPY --chown=agent:agent parse_result.py /usr/local/bin/parse_result.py
RUN chmod +x /usr/local/bin/run_agent.sh /usr/local/bin/parse_result.py

# Switch to non-root user
USER agent

ENV PYTHONUNBUFFERED=1
ENV HOME=/home/agent

ENTRYPOINT ["/usr/local/bin/run_agent.sh"]

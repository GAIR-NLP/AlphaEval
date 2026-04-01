# Claude Code CLI Docker Environment
# Uses the Claude Code CLI directly for agent execution

FROM python:3.11-slim

# Build-time proxy args (optional)
ARG http_proxy
ARG https_proxy
ARG no_proxy=localhost,127.0.0.1

# Install system dependencies (without nodejs/npm from apt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    ca-certificates \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js from official source
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Create non-root user (required for --dangerously-skip-permissions)
RUN apt-get update && apt-get install -y --no-install-recommends sudo && rm -rf /var/lib/apt/lists/* && \
    useradd -m -s /bin/bash agent && \
    echo "agent ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    mkdir -p /workspace /home/agent/.claude /agent_logs && \
    chown -R agent:agent /workspace /home/agent /agent_logs

WORKDIR /workspace

# Install Python dependencies (including PyTorch for code execution tasks)
RUN pip install --no-cache-dir pyyaml torch --extra-index-url https://download.pytorch.org/whl/cpu

# Copy runner script
COPY --chown=agent:agent run_agent.sh /usr/local/bin/run_agent.sh
COPY --chown=agent:agent parse_result.py /usr/local/bin/parse_result.py
RUN chmod +x /usr/local/bin/run_agent.sh /usr/local/bin/parse_result.py

# Switch to non-root user
USER agent

ENV PYTHONUNBUFFERED=1
ENV HOME=/home/agent

ENTRYPOINT ["/usr/local/bin/run_agent.sh"]


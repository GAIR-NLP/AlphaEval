# Cursor Agent Docker Environment
# Uses the Cursor Agent CLI for agent execution

FROM python:3.11-slim

# Build-time proxy args (optional)
ARG http_proxy
ARG https_proxy
ARG no_proxy=localhost,127.0.0.1

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    ca-certificates \
    jq \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/node /usr/local/bin/node

# Create non-root user first
RUN useradd -m -s /bin/bash agent && \
    mkdir -p /workspace /home/agent/.local/bin /agent_logs && \
    chown -R agent:agent /workspace /home/agent /agent_logs

# Install Cursor Agent CLI as agent user (uses official installer)
USER agent
WORKDIR /home/agent
RUN curl https://cursor.com/install -fsS | bash && \
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && \
    . ~/.bashrc

# Set PATH for agent user
ENV PATH="/home/agent/.local/bin:$PATH"
ENV HOME=/home/agent

# Switch back to root to install Python packages and copy scripts
USER root
WORKDIR /workspace

# Install minimal Python dependencies
RUN pip install --no-cache-dir pyyaml

# Copy runner script
COPY --chown=agent:agent run_agent.sh /usr/local/bin/run_agent.sh
COPY --chown=agent:agent parse_result.py /usr/local/bin/parse_result.py
RUN chmod +x /usr/local/bin/run_agent.sh /usr/local/bin/parse_result.py

# Switch to non-root user
USER agent
WORKDIR /workspace

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/usr/local/bin/run_agent.sh"]

#!/bin/bash
# Claude Code CLI Runner (参考 projdevbench 实现)
#
# Environment variables:
#   ANTHROPIC_API_KEY: Anthropic API key
#   ANTHROPIC_BASE_URL: Custom base URL (optional)
#   TASK_PROMPT: The task prompt to execute
#   MODEL_NAME: Model to use (default: gzy/claude-4.5-sonnet)

set -e

echo "=== Claude Code CLI Runner ==="

# Get configuration
MODEL_NAME="${MODEL_NAME:-claude-sonnet-4-5-20250929}"
TASK_PROMPT="${TASK_PROMPT:-}"

# Try reading task from file if not provided
if [ -z "$TASK_PROMPT" ] && [ -f "/workspace/query/task.md" ]; then
    TASK_PROMPT=$(cat /workspace/query/task.md)
fi

if [ -z "$TASK_PROMPT" ]; then
    echo "Error: No task prompt provided" >&2
    exit 1
fi

# Use ANTHROPIC_AUTH_TOKEN if provided, otherwise use ANTHROPIC_API_KEY
if [ -n "$ANTHROPIC_AUTH_TOKEN" ]; then
    export ANTHROPIC_API_KEY="$ANTHROPIC_AUTH_TOKEN"
elif [ -n "$ANTHROPIC_API_KEY" ]; then
    export ANTHROPIC_API_KEY
else
    echo "Error: ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY required" >&2
    exit 1
fi

# Set ANTHROPIC_BASE_URL if provided
if [ -n "$ANTHROPIC_BASE_URL" ]; then
    unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
    export ANTHROPIC_BASE_URL
    echo "Using custom ANTHROPIC_BASE_URL: ${ANTHROPIC_BASE_URL}"
fi

# 配置 Claude settings.json (参考 projdevbench)
echo "Configuring Claude model: $MODEL_NAME"
mkdir -p ~/.claude
cat <<EOT > ~/.claude/settings.json
{
  "env": {
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "$MODEL_NAME",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "$MODEL_NAME",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "$MODEL_NAME"
  }
}
EOT

echo "Model: $MODEL_NAME"
echo "Task: ${TASK_PROMPT:0:100}..."
echo ""

# Build the full prompt with workspace info
FULL_PROMPT="You are working in /workspace with the following structure:
- /workspace/query/        : Task inputs (read this first if task.md exists)
- /workspace/deliverables/ : Input files provided for the task
- /workspace/results/      : Save your final answer here

Complete the task and save your final answer to /workspace/results/ans.md

Task:
$TASK_PROMPT"

# Create log directory
mkdir -p /agent_logs

# Run Claude Code CLI
echo "Running Claude Code CLI..."
cd /workspace

# 参考 projdevbench: 设置所有模型环境变量
export ANTHROPIC_MODEL="${MODEL_NAME}"
export ANTHROPIC_SMALL_FAST_MODEL="${MODEL_NAME}"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="${MODEL_NAME}"
export ANTHROPIC_DEFAULT_SONNET_MODEL="${MODEL_NAME}"
export ANTHROPIC_DEFAULT_OPUS_MODEL="${MODEL_NAME}"

# Log the command being run
echo "claude -p \"${FULL_PROMPT}\" --model \"${MODEL_NAME}\" --output-format stream-json --dangerously-skip-permissions --verbose" > /agent_logs/command.txt

# Run and capture output
claude \
    -p "${FULL_PROMPT}" \
    --model "${MODEL_NAME}" \
    --output-format stream-json \
    --dangerously-skip-permissions \
    --verbose \
    2>&1 | tee /agent_logs/claude_output.jsonl

# Parse the result
echo ""
echo "=== Parsing Results ==="
python3 /usr/local/bin/parse_result.py /agent_logs/claude_output.jsonl

# Copy logs to mounted workspace so they persist after container removal
cp -r /agent_logs/* /workspace/logs/ 2>/dev/null || true

echo ""
echo "=== Execution Complete ==="

#!/bin/bash
# Copilot Agent Runner (参考 projdevbench 实现)
#
# Environment variables:
#   GITHUB_TOKEN: GitHub token for Copilot
#   COPILOT_API_KEY: Alternative Copilot API key
#   TASK_PROMPT: The task prompt to execute
#   MODEL_NAME: Model to use (default: claude-sonnet-4.5)

set -e

echo "=== Copilot Agent Runner ==="

# Get configuration
MODEL_NAME="${MODEL_NAME:-}"
TASK_PROMPT="${TASK_PROMPT:-}"

# Try reading task from file if not provided
if [ -z "$TASK_PROMPT" ] && [ -f "/workspace/query/task.md" ]; then
    TASK_PROMPT=$(cat /workspace/query/task.md)
fi

if [ -z "$TASK_PROMPT" ]; then
    echo "Error: No task prompt provided" >&2
    exit 1
fi

# Configure Copilot API
if [ -n "${COPILOT_API_KEY}" ]; then
    export COPILOT_API_KEY="${COPILOT_API_KEY}"
    echo "Using COPILOT_API_KEY"
elif [ -n "${GITHUB_TOKEN}" ]; then
    export GITHUB_TOKEN="${GITHUB_TOKEN}"
    echo "Using GITHUB_TOKEN"
else
    echo "Warning: No COPILOT_API_KEY or GITHUB_TOKEN provided, may fail" >&2
fi

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

# Run Copilot CLI
echo "Running Copilot CLI..."
# 使用 /workspace 作为工作目录，让 Copilot 能访问 results/ 目录
cd /workspace

# 参考 projdevbench: copilot -p "${PROMPT}" --model "${MODEL_NAME}" --allow-all-tools --allow-all-paths
if command -v copilot &> /dev/null; then
    COPILOT_ARGS=(-p "${FULL_PROMPT}" --allow-all-tools --allow-all-paths)
    if [ -n "$MODEL_NAME" ]; then
        COPILOT_ARGS+=(--model "${MODEL_NAME}")
    fi
    echo "copilot ${COPILOT_ARGS[*]}" > /agent_logs/command.txt
    copilot "${COPILOT_ARGS[@]}" \
        2>&1 | tee /agent_logs/copilot_output.jsonl
else
    echo "Copilot CLI not found"
    echo '{"type": "result", "subtype": "error", "error": "Copilot CLI not available"}' > /agent_logs/copilot_output.jsonl
fi

# Parse the result
echo ""
echo "=== Parsing Results ==="
python3 /usr/local/bin/parse_result.py /agent_logs/copilot_output.jsonl copilot-agent

# Copy logs to mounted workspace so they persist after container removal
cp -r /agent_logs/* /workspace/logs/ 2>/dev/null || true

echo ""
echo "=== Execution Complete ==="

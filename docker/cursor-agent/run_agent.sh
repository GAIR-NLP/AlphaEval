#!/bin/bash
# Cursor Agent Runner
#
# Environment variables:
#   CURSOR_API_KEY: Cursor API key
#   TASK_PROMPT: The task prompt to execute
#   MODEL_NAME: Model to use (default: grok)

set -e

# Ensure PATH includes ~/.local/bin for cursor agent
export PATH="$HOME/.local/bin:$PATH"

echo "=== Cursor Agent Runner ==="

# Get configuration
MODEL_NAME="${MODEL_NAME:-grok}"
TASK_PROMPT="${TASK_PROMPT:-}"

# Try reading task from file if not provided
if [ -z "$TASK_PROMPT" ] && [ -f "/workspace/query/task.md" ]; then
    TASK_PROMPT=$(cat /workspace/query/task.md)
fi

if [ -z "$TASK_PROMPT" ]; then
    echo "Error: No task prompt provided" >&2
    exit 1
fi

# Check for API key
if [ -z "$CURSOR_API_KEY" ]; then
    echo "Error: CURSOR_API_KEY required" >&2
    exit 1
fi

export CURSOR_API_KEY

echo "Model: ${MODEL_NAME:-default}"
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

# Run Cursor Agent CLI
echo "Running Cursor Agent..."
cd /workspace

# Build command
CMD="agent --force -p \"${FULL_PROMPT}\" --output-format json"

if [ -n "$MODEL_NAME" ]; then
    CMD="$CMD --model \"${MODEL_NAME}\""
fi

# Log the command being run
echo "$CMD" > /agent_logs/command.txt

# Run and capture output
eval "$CMD" 2>&1 | tee /agent_logs/cursor_output.jsonl

# Parse the result
echo ""
echo "=== Parsing Results ==="
python3 /usr/local/bin/parse_result.py /agent_logs/cursor_output.jsonl

# Copy logs to mounted workspace so they persist after container removal
cp -r /agent_logs/* /workspace/logs/ 2>/dev/null || true

echo ""
echo "=== Execution Complete ==="


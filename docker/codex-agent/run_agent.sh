#!/bin/bash
# Codex Agent Runner (参考 projdevbench 实现)
#
# Environment variables:
#   CODEX_API_KEY: OpenAI/Codex API key
#   CODEX_BASE_URL: Base URL for Codex API (optional)
#   OPENAI_API_KEY: Alternative OpenAI API key
#   OPENAI_BASE_URL: Alternative base URL
#   TASK_PROMPT: The task prompt to execute
#   MODEL_NAME: Model to use (default: openai/gpt-5.2)

set -e

echo "=== Codex Agent Runner ==="

# Get configuration
MODEL_NAME="${MODEL_NAME:-openai/gpt-5.2}"
TASK_PROMPT="${TASK_PROMPT:-}"

# Try reading task from file if not provided
if [ -z "$TASK_PROMPT" ] && [ -f "/workspace/query/task.md" ]; then
    TASK_PROMPT=$(cat /workspace/query/task.md)
fi

if [ -z "$TASK_PROMPT" ]; then
    echo "Error: No task prompt provided" >&2
    exit 1
fi

# Configure Codex API (参考 projdevbench)
# 确定 API key 和 base URL
API_KEY="${CODEX_API_KEY:-$OPENAI_API_KEY}"
BASE_URL="${CODEX_BASE_URL:-$OPENAI_BASE_URL}"

if [ -z "${API_KEY}" ]; then
    echo "Error: CODEX_API_KEY or OPENAI_API_KEY required" >&2
    exit 1
fi

# 统一使用 OPENAI_API_KEY 环境变量（Codex CLI 使用这个）
export OPENAI_API_KEY="${API_KEY}"

# 如果 BASE_URL 设置了，始终导出 OPENAI_BASE_URL 并配置 config.toml
# 重要：codex-cli 需要 config.toml 才能正确使用自定义 base_url，即使是 gpt 模型
if [ -n "${BASE_URL}" ]; then
    export OPENAI_BASE_URL="${BASE_URL}"
    echo "Using custom API endpoint"
    echo "  BASE_URL: ${BASE_URL}"
    echo "  MODEL: ${MODEL_NAME}"
    
    # 始终创建 config.toml 以确保 base_url 生效
    mkdir -p ~/.codex
    cat <<EOT > ~/.codex/config.toml
model_provider="provider1"
model="${MODEL_NAME}"
preferred_auth_method = "apikey"
[model_providers.provider1]
name = "testoj"
base_url = "${BASE_URL}"
env_key = "OPENAI_API_KEY"
EOT
    echo ""
    echo "Config written to ~/.codex/config.toml:"
    cat ~/.codex/config.toml
else
    echo "Using default OpenAI API"
    echo "  MODEL: ${MODEL_NAME}"
fi

echo "Codex API configured"
echo "Model: $MODEL_NAME"
echo "Task: ${TASK_PROMPT:0:100}..."
echo ""

# Build the full prompt with workspace info
FULL_PROMPT="You are working in /workspace with the following structure:
- /workspace/query/        : Task inputs (read this first if task.md exists)
- /workspace/deliverables/ : Your working directory
- /workspace/results/      : Save your final answer here
- /workspace/context/      : Additional context files

Complete the task and save your final answer to /workspace/results/ans.md

Task:
$TASK_PROMPT"

# Create log directory
mkdir -p /workspace/logs

# Run Codex CLI
echo "Running Codex CLI..."
cd /workspace/deliverables

# Run and capture output (参考 projdevbench)
# 正确的参数顺序: codex exec "prompt" --model xxx --json --其他参数
codex exec "${FULL_PROMPT}" \
    --model "${MODEL_NAME}" \
    --json \
    --skip-git-repo-check \
    --dangerously-bypass-approvals-and-sandbox \
    2>&1 | tee /workspace/logs/codex_output.jsonl

# Parse the result
echo ""
echo "=== Parsing Results ==="
python3 /usr/local/bin/parse_result.py /workspace/logs/codex_output.jsonl codex-agent

echo ""
echo "=== Execution Complete ==="

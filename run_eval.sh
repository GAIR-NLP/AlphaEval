#!/bin/bash
# AgentEval Runner - Supports multiple agent environments
#
# Usage:
#   ./run_eval.sh <agent_type> <task_id>
#
# Agent types:
#   - claude-agent-sdk : Uses Claude Agent SDK (Python)
#   - claude-code      : Uses Claude Code CLI directly
#
# Examples:
#   ./run_eval.sh claude-agent-sdk math_5_plus_4
#   ./run_eval.sh claude-code math_5_plus_4

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$SCRIPT_DIR/docker"
TASKS_DIR="$SCRIPT_DIR/tasks"
EVALS_DIR="$SCRIPT_DIR/evals"

# Parse arguments
AGENT_TYPE="${1:-claude-agent-sdk}"
TASK_ID="${2:-math_5_plus_4}"

# Set default model based on agent type
if [ -z "$MODEL_NAME" ]; then
    case "$AGENT_TYPE" in
        cursor-agent)
            MODEL_NAME="grok"
            ;;
        codex-agent)
            MODEL_NAME="openai/gpt-5.2"
            ;;
        gemini-agent)
            MODEL_NAME="gemini-3-pro-preview"
            ;;
        copilot-agent)
            MODEL_NAME="gpt-5"
            ;;
        claude-code)
            MODEL_NAME="claude-sonnet-4-5-20250929"
            ;;
        *)
            MODEL_NAME="gzy/claude-4.5-sonnet"
            ;;
    esac
fi

echo -e "${GREEN}🚀 AgentEval Runner${NC}"
echo "================================"
echo -e "Agent:  ${BLUE}${AGENT_TYPE}${NC}"
echo -e "Task:   ${YELLOW}${TASK_ID}${NC}"
echo -e "Model:  ${MODEL_NAME}"
echo ""

# Validate agent type
if [[ ! "$AGENT_TYPE" =~ ^(claude-agent-sdk|claude-code|cursor-agent|codex-agent|gemini-agent|copilot-agent)$ ]]; then
    echo -e "${RED}❌ Error: Unknown agent type: ${AGENT_TYPE}${NC}"
    echo "Available agents: claude-agent-sdk, claude-code, cursor-agent, codex-agent, gemini-agent, copilot-agent"
    exit 1
fi

# Check for API key based on agent type
if [ "$AGENT_TYPE" = "cursor-agent" ]; then
    if [ -z "$CURSOR_API_KEY" ]; then
        echo -e "${RED}❌ Error: CURSOR_API_KEY not set${NC}"
        echo ""
        echo "Please set your API key:"
        echo "  export CURSOR_API_KEY=your-cursor-api-key"
        exit 1
    fi
    echo -e "${GREEN}✓ Cursor API key found${NC}"
elif [ "$AGENT_TYPE" = "codex-agent" ]; then
    if [ -z "$CODEX_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$MINIMAX_API_KEY" ] && [ -z "$DASHSCOPE_API_KEY" ]; then
        echo -e "${RED}❌ Error: CODEX_API_KEY/OPENAI_API_KEY/MINIMAX_API_KEY/DASHSCOPE_API_KEY not set${NC}"
        echo ""
        echo "Please set your API key:"
        echo "  export CODEX_API_KEY=your-codex-api-key"
        exit 1
    fi
    echo -e "${GREEN}✓ Codex API key found${NC}"
elif [ "$AGENT_TYPE" = "gemini-agent" ]; then
    if [ -z "$GEMINI_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ]; then
        echo -e "${RED}❌ Error: GEMINI_API_KEY or GOOGLE_API_KEY not set${NC}"
        echo ""
        echo "Please set your API key:"
        echo "  export GEMINI_API_KEY=your-gemini-api-key"
        exit 1
    fi
    echo -e "${GREEN}✓ Gemini API key found${NC}"
elif [ "$AGENT_TYPE" = "copilot-agent" ]; then
    if [ -z "$COPILOT_API_KEY" ] && [ -z "$GITHUB_TOKEN" ]; then
        echo -e "${YELLOW}⚠️ Warning: COPILOT_API_KEY or GITHUB_TOKEN not set, may fail${NC}"
    else
        echo -e "${GREEN}✓ Copilot API key found${NC}"
    fi
else
    if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$ANTHROPIC_AUTH_TOKEN" ]; then
        echo -e "${RED}❌ Error: ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN not set${NC}"
        echo ""
        echo "Please set your API key:"
        echo "  export ANTHROPIC_API_KEY=your-api-key"
        exit 1
    fi
    echo -e "${GREEN}✓ API key found${NC}"
fi

# Check if task exists
TASK_PATH="$TASKS_DIR/$TASK_ID"
if [ ! -d "$TASK_PATH" ]; then
    echo -e "${RED}❌ Error: Task not found: ${TASK_ID}${NC}"
    echo "Available tasks:"
    ls -1 "$TASKS_DIR"
    exit 1
fi
echo -e "${GREEN}✓ Task found: ${TASK_PATH}${NC}"

# Create run directory with model tag
_MODEL_TAG="${CODEX_MODEL_NAME:-${COPILOT_MODEL_NAME:-${CURSOR_MODEL_NAME:-${MODEL_NAME:-unknown}}}}"
_MODEL_TAG="${_MODEL_TAG//\//-}"
RUN_ID="run_$(date +%Y%m%d_%H%M%S)_${AGENT_TYPE}_${_MODEL_TAG}_$$"
RUN_DIR="$EVALS_DIR/$TASK_ID/$RUN_ID"
WORKSPACE_DIR="$RUN_DIR/workspace"
mkdir -p "$WORKSPACE_DIR"/{query,deliverables,results,logs}

# Copy task files to workspace
echo ""
echo "Setting up workspace..."

# Copy query
if [ -f "$TASK_PATH/query.md" ]; then
    cp "$TASK_PATH/query.md" "$WORKSPACE_DIR/query/task.md"
fi

# Copy files to deliverables (new unified approach)
if [ -d "$TASK_PATH/files" ]; then
    cp -r "$TASK_PATH/files"/* "$WORKSPACE_DIR/deliverables/" 2>/dev/null || true
fi

# Backward compatibility: also support old initial/ and context/ directories
if [ -d "$TASK_PATH/initial" ]; then
    cp -r "$TASK_PATH/initial"/* "$WORKSPACE_DIR/deliverables/" 2>/dev/null || true
fi
if [ -d "$TASK_PATH/context" ]; then
    cp -r "$TASK_PATH/context"/* "$WORKSPACE_DIR/deliverables/" 2>/dev/null || true
fi

# Set permissions for non-root user in container
chmod -R 777 "$WORKSPACE_DIR"

echo -e "${GREEN}✓ Workspace ready: ${WORKSPACE_DIR}${NC}"

# Read task prompt
TASK_PROMPT=$(cat "$WORKSPACE_DIR/query/task.md")

# Check if Docker image exists, build if not
IMAGE_TAG="${IMAGE_TAG:-latest}"
IMAGE_NAME="agenteval/${AGENT_TYPE}:${IMAGE_TAG}"
if docker image inspect "$IMAGE_NAME" &> /dev/null; then
    echo -e "${GREEN}✓ Docker image found: ${IMAGE_NAME}${NC}"
else
    echo ""
    echo "Building Docker image: ${AGENT_TYPE}..."
    docker build -t "$IMAGE_NAME" "$DOCKER_DIR/${AGENT_TYPE}"
fi

# Run agent in Docker
echo ""
echo "Running agent..."
echo "================================"

# Set up environment variables based on agent type
AGENT_MODEL_NAME="${MODEL_NAME}"
if [ "$AGENT_TYPE" = "codex-agent" ] && [ -n "$CODEX_MODEL_NAME" ]; then
    AGENT_MODEL_NAME="$CODEX_MODEL_NAME"
elif [ "$AGENT_TYPE" = "copilot-agent" ] && [ -n "$COPILOT_MODEL_NAME" ]; then
    AGENT_MODEL_NAME="$COPILOT_MODEL_NAME"
elif [ "$AGENT_TYPE" = "cursor-agent" ] && [ -n "$CURSOR_MODEL_NAME" ]; then
    AGENT_MODEL_NAME="$CURSOR_MODEL_NAME"
fi

DOCKER_ENV_ARGS=(
    -e "TASK_PROMPT=${TASK_PROMPT}"
    -e "MODEL_NAME=${AGENT_MODEL_NAME}"
    -e "MAX_TURNS=${MAX_TURNS:-30}"
)

if [ "$AGENT_TYPE" = "cursor-agent" ]; then
    if [ -z "$CURSOR_API_KEY" ]; then
        echo -e "${RED}❌ Error: CURSOR_API_KEY not set for cursor-agent${NC}"
        exit 1
    fi
    DOCKER_ENV_ARGS+=(-e "CURSOR_API_KEY=${CURSOR_API_KEY}")
elif [ "$AGENT_TYPE" = "codex-agent" ]; then
    DOCKER_ENV_ARGS+=(-e "CODEX_API_KEY=${CODEX_API_KEY:-$OPENAI_API_KEY}")
    if [ -n "$CODEX_BASE_URL" ]; then
        DOCKER_ENV_ARGS+=(-e "CODEX_BASE_URL=${CODEX_BASE_URL}")
    elif [ -n "$OPENAI_BASE_URL" ]; then
        DOCKER_ENV_ARGS+=(-e "CODEX_BASE_URL=${OPENAI_BASE_URL}")
    fi
    DOCKER_ENV_ARGS+=(-e "OPENAI_API_KEY=${OPENAI_API_KEY:-$CODEX_API_KEY}")
    [ -n "$OPENAI_BASE_URL" ] && DOCKER_ENV_ARGS+=(-e "OPENAI_BASE_URL=${OPENAI_BASE_URL}")
    [ -n "$MINIMAX_API_KEY" ] && DOCKER_ENV_ARGS+=(-e "MINIMAX_API_KEY=${MINIMAX_API_KEY}")
    [ -n "$DASHSCOPE_API_KEY" ] && DOCKER_ENV_ARGS+=(-e "DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}")
elif [ "$AGENT_TYPE" = "gemini-agent" ]; then
    DOCKER_ENV_ARGS+=(-e "GEMINI_API_KEY=${GEMINI_API_KEY:-$GOOGLE_API_KEY}")
    DOCKER_ENV_ARGS+=(-e "GOOGLE_API_KEY=${GOOGLE_API_KEY:-$GEMINI_API_KEY}")
    [ -n "$GOOGLE_GEMINI_BASE_URL" ] && DOCKER_ENV_ARGS+=(-e "GOOGLE_GEMINI_BASE_URL=${GOOGLE_GEMINI_BASE_URL}")
elif [ "$AGENT_TYPE" = "copilot-agent" ]; then
    [ -n "$COPILOT_API_KEY" ] && DOCKER_ENV_ARGS+=(-e "COPILOT_API_KEY=${COPILOT_API_KEY}")
    [ -n "$GITHUB_TOKEN" ] && DOCKER_ENV_ARGS+=(-e "GITHUB_TOKEN=${GITHUB_TOKEN}")
    # Copilot needs proxy for model availability checks (e.g. claude-opus-4.6)
    DOCKER_ENV_ARGS+=(-e "HTTP_PROXY=${HTTP_PROXY:-http://127.0.0.1:7894}")
    DOCKER_ENV_ARGS+=(-e "HTTPS_PROXY=${HTTPS_PROXY:-http://127.0.0.1:7894}")
    DOCKER_ENV_ARGS+=(-e "http_proxy=${http_proxy:-http://127.0.0.1:7894}")
    DOCKER_ENV_ARGS+=(-e "https_proxy=${https_proxy:-http://127.0.0.1:7894}")
else
    DOCKER_ENV_ARGS+=(-e "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}")
    DOCKER_ENV_ARGS+=(-e "ANTHROPIC_AUTH_TOKEN=${ANTHROPIC_AUTH_TOKEN:-$ANTHROPIC_API_KEY}")
    [ -n "$ANTHROPIC_BASE_URL" ] && DOCKER_ENV_ARGS+=(-e "ANTHROPIC_BASE_URL=${ANTHROPIC_BASE_URL}")
fi

DOCKER_RUN_ARGS=(--rm --network host)

docker run "${DOCKER_RUN_ARGS[@]}" \
    "${DOCKER_ENV_ARGS[@]}" \
    -v "${WORKSPACE_DIR}:/workspace" \
    -v "${DOCKER_DIR}/${AGENT_TYPE}/run_agent.sh:/usr/local/bin/run_agent.sh:ro" \
    "${IMAGE_NAME}"
DOCKER_EXIT=$?

echo "================================"

# If agent ran (exit 0 or timeout 124) but no ans.md, create placeholder
# This marks the run as "agent completed" so it won't be retried
if [ ! -f "${WORKSPACE_DIR}/results/ans.md" ]; then
    mkdir -p "${WORKSPACE_DIR}/results"
    if [ $DOCKER_EXIT -eq 0 ] || [ $DOCKER_EXIT -eq 124 ]; then
        echo "(Agent completed without producing answer - docker exit code: $DOCKER_EXIT)" > "${WORKSPACE_DIR}/results/ans.md"
        echo "Note: Agent ran but did not produce ans.md, created placeholder"
    fi
fi

# Skip evaluation if requested
if [ "${SKIP_EVALUATION:-0}" = "1" ]; then
    echo ""
    echo -e "${GREEN}✓ Agent run complete (evaluation skipped)${NC}"
    echo "Results saved to: ${RUN_DIR}"
    exit 0
fi

# Parse task.yaml for evaluation config using Python (more reliable)
EVAL_TYPE="exact_match"
EXPECTED_ANSWER=""
REFERENCE_ANSWER=""
JUDGE_MODEL="openai/gpt-4o"

if [ -f "$TASK_PATH/task.yaml" ]; then
    EVAL_TYPE=$(python "$SCRIPT_DIR/scripts/parse_task.py" "$TASK_PATH/task.yaml" eval_type 2>/dev/null || echo "exact_match")
    EXPECTED_ANSWER=$(python "$SCRIPT_DIR/scripts/parse_task.py" "$TASK_PATH/task.yaml" expected_answer 2>/dev/null || echo "")
    REFERENCE_ANSWER=$(python "$SCRIPT_DIR/scripts/parse_task.py" "$TASK_PATH/task.yaml" reference_answer 2>/dev/null || echo "")
    JUDGE_MODEL=$(python "$SCRIPT_DIR/scripts/parse_task.py" "$TASK_PATH/task.yaml" judge_model 2>/dev/null || echo "openai/gpt-4o")
fi

# Get actual answer
ACTUAL_ANSWER=""
if [ -f "$WORKSPACE_DIR/results/ans.md" ]; then
    ACTUAL_ANSWER=$(cat "$WORKSPACE_DIR/results/ans.md")
    ACTUAL_ANSWER_CLEAN=$(echo "$ACTUAL_ANSWER" | tr -d '[:space:]')
fi

# Evaluate based on type
echo ""
echo "=== EVALUATION ==="
echo -e "Type:     ${BLUE}${EVAL_TYPE}${NC}"

SCORE=0.0
REASONING=""

if [ "$EVAL_TYPE" = "exact_match" ]; then
    echo "Expected: ${EXPECTED_ANSWER}"
    echo "Actual:   ${ACTUAL_ANSWER_CLEAN}"

    if [ "$EXPECTED_ANSWER" = "$ACTUAL_ANSWER_CLEAN" ]; then
        SCORE=1.0
        REASONING="Exact match"
        echo -e "${GREEN}Score: ${SCORE}${NC}"
    else
        SCORE=0.0
        REASONING="Answer does not match expected value"
        echo -e "${RED}Score: ${SCORE}${NC}"
    fi

elif [ "$EVAL_TYPE" = "llm_judge" ]; then
    echo "Query:     ${TASK_PROMPT:0:100}..."
    echo "Reference: ${REFERENCE_ANSWER}"
    echo "Actual:    ${ACTUAL_ANSWER}"
    echo ""
    echo -e "${YELLOW}Running LLM-as-a-Judge evaluation...${NC}"

    # Run LLM judge (pass query, actual, reference, config)
    JUDGE_RESULT=$(python "$SCRIPT_DIR/scripts/llm_judge.py" \
        "$TASK_PROMPT" \
        "$ACTUAL_ANSWER" \
        "$REFERENCE_ANSWER" \
        --config "$SCRIPT_DIR/config.yaml" \
        2>&1) || true

    echo ""
    echo "Judge Result:"
    echo "$JUDGE_RESULT"

    # Parse result
    PASSED_STR=$(echo "$JUDGE_RESULT" | grep -o '"passed":[^,}]*' | cut -d':' -f2 | tr -d ' ')
    REASONING=$(echo "$JUDGE_RESULT" | grep -o '"reasoning":"[^"]*"' | cut -d':' -f2- | tr -d '"')

    if [ "$PASSED_STR" = "true" ]; then
        SCORE=1.0
    else
        SCORE=0.0
    fi
    echo -e "Score: ${SCORE}"

    # Save judge result
    echo "$JUDGE_RESULT" > "$RUN_DIR/judge_result.json"

elif [ "$EVAL_TYPE" = "code_exec" ]; then
    echo -e "${YELLOW}Running code execution evaluation...${NC}"

    # Get rubric config
    RUBRIC_SCRIPT=$(python "$SCRIPT_DIR/scripts/parse_task.py" "$TASK_PATH/task.yaml" rubric_script 2>/dev/null || echo "")

    # Build full rubric path
    RUBRIC_FULL_PATH="$TASK_PATH/$RUBRIC_SCRIPT"

    echo "Rubric:   ${RUBRIC_FULL_PATH}"
    echo ""

    # Copy entire eval directory to workspace (but outside deliverables so agent can't see it)
    # This includes rubric.py and ground_truth.json
    EVAL_DIR=$(dirname "$RUBRIC_FULL_PATH")
    mkdir -p "$WORKSPACE_DIR/rubric"
    cp -r "$EVAL_DIR"/* "$WORKSPACE_DIR/rubric/"

    # Copy config.yaml to deliverables so rubric can find API key
    cp "$SCRIPT_DIR/config.yaml" "$WORKSPACE_DIR/deliverables/config.yaml" 2>/dev/null || true

    # Run code execution evaluator (score-based)
    EXEC_RESULT=$(python "$SCRIPT_DIR/scripts/code_exec_eval.py" \
        "$WORKSPACE_DIR/rubric/$(basename $RUBRIC_SCRIPT)" \
        "$WORKSPACE_DIR/deliverables" \
        2>&1) || true

    echo "Execution Result:"
    echo "$EXEC_RESULT"

    # Parse result - score is the primary metric
    SCORE=$(echo "$EXEC_RESULT" | grep -o '"score":[^,}]*' | cut -d':' -f2 | tr -d ' ')
    REASONING=$(echo "$EXEC_RESULT" | grep -o '"reasoning":"[^"]*"' | cut -d':' -f2- | tr -d '"')

    # Display score with color coding
    if [ "$(echo "$SCORE >= 0.8" | bc -l 2>/dev/null)" = "1" ]; then
        echo -e "${GREEN}Score: ${SCORE}${NC}"
    elif [ "$(echo "$SCORE >= 0.5" | bc -l 2>/dev/null)" = "1" ]; then
        echo -e "${YELLOW}Score: ${SCORE}${NC}"
    else
        echo -e "${RED}Score: ${SCORE}${NC}"
    fi

    # Save execution result
    echo "$EXEC_RESULT" > "$RUN_DIR/exec_result.json"

else
    echo -e "${RED}Unknown evaluation type: ${EVAL_TYPE}${NC}"
    SCORE=0.0
    REASONING="Unknown evaluation type"
fi

# Save evaluation result
cat > "$RUN_DIR/evaluation.json" << EOF
{
    "task_id": "${TASK_ID}",
    "agent": "${AGENT_TYPE}",
    "model": "${MODEL_NAME}",
    "evaluation_type": "${EVAL_TYPE}",
    "score": ${SCORE:-0},
    "expected": "${EXPECTED_ANSWER:-$REFERENCE_ANSWER}",
    "actual": "${ACTUAL_ANSWER_CLEAN}",
    "reasoning": "${REASONING}",
    "workspace": "${WORKSPACE_DIR}",
    "timestamp": "$(date -Iseconds)"
}
EOF

echo ""
echo -e "${GREEN}✓ Evaluation complete!${NC}"
echo "Results saved to: ${RUN_DIR}"
echo ""
echo "Files:"
ls -la "$RUN_DIR"
echo ""
echo "Workspace:"
ls -la "$WORKSPACE_DIR"


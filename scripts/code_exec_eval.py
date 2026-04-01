#!/usr/bin/env python3
"""Code Execution Evaluator

Runs a rubric script to evaluate agent's code submission.
Score (0.0-1.0) is the primary metric. passed is derived from score > 0.

Usage:
    python code_exec_eval.py <rubric_script> <workspace_dir> [--pass-threshold <float>]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def evaluate_with_code(
    rubric_script: str,
    workspace_dir: str,
    timeout: int = 120,
) -> dict:
    """Run rubric script to evaluate the submission.

    Args:
        rubric_script: Path to the rubric script
        workspace_dir: Path to the agent's workspace (submission)
        timeout: Execution timeout in seconds

    Returns:
        {"score": float, "output": str, "reasoning": str}
    """
    rubric_path = Path(rubric_script)
    workspace_path = Path(workspace_dir)

    if not rubric_path.exists():
        return {
            "score": 0.0,
            "output": "",
            "reasoning": f"Rubric script not found: {rubric_script}"
        }

    if not workspace_path.exists():
        return {
            "score": 0.0,
            "output": "",
            "reasoning": f"Workspace not found: {workspace_dir}"
        }

    try:
        rubric_abs_path = rubric_path.resolve()
        result = subprocess.run(
            ["python3", str(rubric_abs_path), "--submission", str(workspace_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(workspace_path),
        )

        output = result.stdout + result.stderr

        # Extract score from rubric output (primary metric)
        # Try format 1: score=X.X (poet/segment-research style)
        score_match = re.search(r"score=(\d+\.?\d*)", output)
        if score_match:
            score = float(score_match.group(1))
        else:
            # Try format 2: JSON {"score": X.X} (yuhe style)
            score = 0.0
            for line in output.strip().splitlines():
                line = line.strip()
                if line.startswith("{"):
                    try:
                        parsed = json.loads(line)
                        if "score" in parsed:
                            score = float(parsed["score"])
                            break
                    except (json.JSONDecodeError, ValueError):
                        pass

        return {
            "score": score,
            "output": output.strip(),
            "reasoning": f"Score: {score:.2f}",
            "exit_code": result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {
            "score": 0.0,
            "output": "",
            "reasoning": f"Rubric execution timed out after {timeout}s"
        }
    except Exception as e:
        return {
            "score": 0.0,
            "output": "",
            "reasoning": f"Execution error: {str(e)}"
        }


def main():
    parser = argparse.ArgumentParser(description="Code Execution Evaluator")
    parser.add_argument("rubric_script", help="Path to the rubric script")
    parser.add_argument("workspace_dir", help="Path to the workspace/submission")
    parser.add_argument("--timeout", type=int, default=120, help="Execution timeout")
    # Deprecated args kept for backward compat
    parser.add_argument("--pass-pattern", default=None, help="(Deprecated, ignored)")
    parser.add_argument("--pass-threshold", default=None, help="(Deprecated, ignored)")

    args = parser.parse_args()

    result = evaluate_with_code(
        rubric_script=args.rubric_script,
        workspace_dir=args.workspace_dir,
        timeout=args.timeout,
    )

    # Output result as JSON
    print(json.dumps(result, ensure_ascii=False))

    # Always exit 0 - score is the metric, not pass/fail
    sys.exit(0)


if __name__ == "__main__":
    main()


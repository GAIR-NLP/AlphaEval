#!/usr/bin/env python3
"""
Code Execution Evaluation Template — Constraint Verification

Use this template when the agent's output contains verifiable numeric/structured data.
The script extracts the answer from the agent's output and compares against expected values.

Output format (required):
    score=X.XX    (0.00 to 1.00)
    result=PASSED or result=FAILED
"""

import re
import json
import argparse
from pathlib import Path
from typing import Optional


# ============================================================
# CONFIGURATION — Edit these for your task
# ============================================================

EXPECTED_VALUE = 75872          # Expected answer (e.g., total cost)
TOLERANCE = 0.01                # Acceptable relative error (1%)
PASS_THRESHOLD = 0.6            # Minimum score to pass


# ============================================================
# ANSWER EXTRACTION — Customize parsing logic
# ============================================================

def extract_answer(text: str) -> Optional[float]:
    """Extract the agent's answer from its output text.

    Customize the regex patterns to match your expected output format.
    """
    patterns = [
        r'[Tt]otal\s*[Cc]ost[：:]\s*[￥¥$]?\s*([\d,]+(?:\.\d+)?)',
        r'答案[：:]\s*([\d,]+(?:\.\d+)?)',
        r'结果[：:]\s*([\d,]+(?:\.\d+)?)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            value_str = match.group(1).replace(',', '')
            try:
                return float(value_str)
            except ValueError:
                continue
    return None


# ============================================================
# SCORING — Customize evaluation logic
# ============================================================

def compute_score(extracted_value: Optional[float]) -> dict:
    """Compute score based on extracted answer.

    Returns dict with:
        - score: float (0.0 to 1.0)
        - reasoning: str (explanation)
    """
    if extracted_value is None:
        return {"score": 0.0, "reasoning": "Could not extract answer from output"}

    # Check if answer matches expected value within tolerance
    if EXPECTED_VALUE == 0:
        exact_match = (extracted_value == 0)
    else:
        relative_error = abs(extracted_value - EXPECTED_VALUE) / abs(EXPECTED_VALUE)
        exact_match = relative_error <= TOLERANCE

    if exact_match:
        return {"score": 1.0, "reasoning": f"Correct: {extracted_value} matches expected {EXPECTED_VALUE}"}
    else:
        return {"score": 0.0, "reasoning": f"Incorrect: got {extracted_value}, expected {EXPECTED_VALUE}"}


# ============================================================
# MAIN — Usually no need to modify
# ============================================================

def find_answer_file(workspace_dir: str) -> Optional[str]:
    """Find the agent's answer file."""
    for base in [workspace_dir, str(Path(workspace_dir).parent)]:
        ans_path = Path(base) / "results" / "ans.md"
        if ans_path.exists():
            return ans_path.read_text(encoding='utf-8')
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", required=True, help="Submission directory")
    args = parser.parse_args()

    answer_text = find_answer_file(args.submission)
    if not answer_text:
        print("No answer file found at results/ans.md")
        print("score=0.00")
        print("result=FAILED")
        return

    extracted = extract_answer(answer_text)
    result = compute_score(extracted)

    passed = result["score"] >= PASS_THRESHOLD
    print(result["reasoning"])
    print(f"score={result['score']:.2f}")
    print(f"result={'PASSED' if passed else 'FAILED'}")


if __name__ == "__main__":
    main()

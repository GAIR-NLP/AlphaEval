#!/usr/bin/env python3
"""
BOM Procurement Optimization — Constraint Verification Evaluation

Extracts the total cost from the agent's answer and compares against the expected optimal cost.
Binary scoring: 1.0 if cost matches (within tolerance), 0.0 otherwise.
"""

import re
import argparse
from pathlib import Path
from typing import Optional

# ============================================================
# CONFIGURATION — Set the expected optimal cost for your task
# ============================================================

EXPECTED_COST = 75872       # Expected total procurement cost
TOLERANCE = 0.01            # 1% tolerance for floating point
PASS_THRESHOLD = 0.6


def extract_cost_from_text(text: str) -> Optional[float]:
    """Extract total cost from agent output."""
    patterns = [
        r'[Tt]otal\s*[Cc]ost[：:]\s*[$￥¥]?\s*([\d,]+(?:\.\d+)?)',
        r'[Tt]otal[：:]\s*[$￥¥]?\s*([\d,]+(?:\.\d+)?)',
        r'[$]\s*([\d,]+(?:\.\d+)?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except ValueError:
                continue
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", required=True)
    args = parser.parse_args()

    ans_path = Path(args.submission) / "results" / "ans.md"
    if not ans_path.exists():
        ans_path = Path(args.submission).parent / "results" / "ans.md"

    if not ans_path.exists():
        print("No answer file found")
        print("score=0.00")
        print("result=FAILED")
        return

    text = ans_path.read_text(encoding='utf-8')
    cost = extract_cost_from_text(text)

    if cost is None:
        print("Could not extract total cost from answer")
        print("score=0.00")
        print("result=FAILED")
        return

    relative_error = abs(cost - EXPECTED_COST) / EXPECTED_COST if EXPECTED_COST != 0 else 0
    is_correct = relative_error <= TOLERANCE

    print(f"Expected cost: ${EXPECTED_COST}")
    print(f"Extracted cost: ${cost}")
    print(f"Relative error: {relative_error:.2%}")
    print(f"score={'1.00' if is_correct else '0.00'}")
    print(f"result={'PASSED' if is_correct else 'FAILED'}")


if __name__ == "__main__":
    main()

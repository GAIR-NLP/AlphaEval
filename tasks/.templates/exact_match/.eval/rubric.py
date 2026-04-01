#!/usr/bin/env python3
"""
Exact Match Evaluation Template

Use this template when the answer is a single value that must match exactly.
Supports numeric comparison with tolerance and string normalization.

Output format (required):
    score=X.XX    (0.00 or 1.00)
    result=PASSED or result=FAILED
"""

import re
import argparse
from pathlib import Path
from typing import Optional


# ============================================================
# CONFIGURATION — Edit these for your task
# ============================================================

EXPECTED_ANSWER = "42"          # Expected answer (string)
NUMERIC_MODE = True             # True: compare as numbers; False: compare as strings
TOLERANCE = 0.001               # Numeric tolerance (ignored if NUMERIC_MODE=False)
CASE_SENSITIVE = False          # String comparison case sensitivity


# ============================================================
# EVALUATION LOGIC
# ============================================================

def extract_answer(text: str) -> str:
    """Extract the answer from agent output. Handles common formats."""
    text = text.strip()

    # Try to find a boxed answer: \boxed{...}
    boxed = re.search(r'\\boxed\{([^}]+)\}', text)
    if boxed:
        return boxed.group(1).strip()

    # Try "Answer: X" or "答案：X" format
    answer_match = re.search(r'(?:Answer|答案|Result|结果)[：:]\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if answer_match:
        return answer_match.group(1).strip()

    # If short enough, use the entire text
    if len(text) < 100:
        return text

    # Use the last line
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    return lines[-1] if lines else ""


def normalize(s: str) -> str:
    """Normalize a string for comparison."""
    s = s.strip()
    s = re.sub(r'[,，\s]+', '', s)      # Remove commas, spaces
    s = re.sub(r'[。.]+$', '', s)        # Remove trailing periods
    if not CASE_SENSITIVE:
        s = s.lower()
    return s


def compare(extracted: str, expected: str) -> bool:
    """Compare extracted answer against expected."""
    if NUMERIC_MODE:
        try:
            ext_num = float(normalize(extracted))
            exp_num = float(normalize(expected))
            return abs(ext_num - exp_num) <= TOLERANCE * max(abs(exp_num), 1e-10)
        except ValueError:
            pass

    # Fall back to string comparison
    return normalize(extracted) == normalize(expected)


# ============================================================
# MAIN
# ============================================================

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
    extracted = extract_answer(text)
    is_correct = compare(extracted, EXPECTED_ANSWER)

    print(f"Expected: {EXPECTED_ANSWER}")
    print(f"Extracted: {extracted}")
    print(f"Match: {is_correct}")
    print(f"score={'1.00' if is_correct else '0.00'}")
    print(f"result={'PASSED' if is_correct else 'FAILED'}")


if __name__ == "__main__":
    main()

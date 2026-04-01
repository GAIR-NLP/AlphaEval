#!/usr/bin/env python3
"""
Hybrid Evaluation Template — LLM-as-Judge + Numerical Verification

Use this template when the answer requires BOTH:
  1. Numerical accuracy (verified programmatically)
  2. Qualitative analysis quality (verified by LLM-as-Judge)

The final score is a weighted combination of both components.

Output format (required):
    score=X.XX    (0.00 to 1.00)
    result=PASSED or result=FAILED
"""

import re
import os
import sys
import json
import argparse
import yaml
from pathlib import Path
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)


# ============================================================
# CONFIGURATION
# ============================================================

PASS_THRESHOLD = 0.6
NUMERICAL_WEIGHT = 0.5          # Weight for numerical checks (0-1)
RUBRIC_WEIGHT = 0.5             # Weight for rubric checks (0-1)
MAX_ANSWER_LENGTH = 30000


# ============================================================
# CONFIG & FILE LOADING
# ============================================================

def load_config():
    config_paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "config.yaml"),
        os.path.join(os.getcwd(), "config.yaml"),
    ]
    for p in config_paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    return {}


def find_answer_file(workspace_dir: str) -> Optional[str]:
    for base in [workspace_dir, str(Path(workspace_dir).parent)]:
        ans_path = Path(base) / "results" / "ans.md"
        if ans_path.exists():
            return ans_path.read_text(encoding='utf-8')
    return None


# ============================================================
# PART 1: NUMERICAL VERIFICATION
# ============================================================

def check_numerical(text: str, checks: list) -> dict:
    """Verify numerical values in the answer.

    Returns:
        dict with 'score' (0-1), 'details' (list of per-check results)
    """
    total_weight = 0
    passed_weight = 0
    details = []

    for check in checks:
        name = check["name"]
        expected = check["expected"]
        tolerance = check.get("tolerance", 0.01)
        weight = check.get("weight", 1)
        pattern = check.get("extraction_pattern", "")

        total_weight += weight

        # Extract value
        match = re.search(pattern, text) if pattern else None
        if match:
            try:
                extracted = float(match.group(1).replace(',', ''))
                if tolerance == 0:
                    is_correct = (extracted == expected)
                else:
                    is_correct = abs(extracted - expected) <= tolerance * max(abs(expected), 1e-10)

                if is_correct:
                    passed_weight += weight
                    details.append(f"  [PASS] {name}: got {extracted}, expected {expected}")
                else:
                    details.append(f"  [FAIL] {name}: got {extracted}, expected {expected}")
            except ValueError:
                details.append(f"  [FAIL] {name}: could not parse '{match.group(1)}'")
        else:
            details.append(f"  [FAIL] {name}: value not found in output")

    score = passed_weight / total_weight if total_weight > 0 else 0
    return {"score": score, "details": details}


# ============================================================
# PART 2: LLM-AS-JUDGE RUBRIC
# ============================================================

def check_rubric(text: str, question: str, rubric_checks: list) -> dict:
    """Evaluate qualitative aspects via LLM-as-Judge.

    Returns:
        dict with 'score' (0-1), 'details' (list of per-check results)
    """
    config = load_config()
    llm_config = config.get("llm", {})
    client = OpenAI(
        api_key=llm_config.get("api_key", os.environ.get("OPENAI_API_KEY", "")),
        base_url=llm_config.get("base_url", "https://api.openai.com/v1"),
    )
    model = llm_config.get("judge_model", "gpt-4o")

    total_weight = 0
    passed_weight = 0
    details = []

    for i, check in enumerate(rubric_checks):
        point = check["point"]
        weight = check.get("weight", 1)
        total_weight += weight

        prompt = f"""Judge whether this AI response covers the criterion.
Answer "yes" or "no" on the first line.

Question: {question}
Criterion: {point}
Response: {text[:MAX_ANSWER_LENGTH]}"""

        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.0,
            )
            result = resp.choices[0].message.content.strip()
            is_covered = result.split('\n')[0].lower().startswith('yes')
            if is_covered:
                passed_weight += weight
                details.append(f"  [PASS] Rubric {i+1}: {point[:60]}...")
            else:
                details.append(f"  [FAIL] Rubric {i+1}: {point[:60]}...")
        except Exception as e:
            details.append(f"  [ERR]  Rubric {i+1}: {str(e)[:60]}")

    score = passed_weight / total_weight if total_weight > 0 else 0
    return {"score": score, "details": details}


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", required=True)
    args = parser.parse_args()

    # Load config
    rubric_path = Path(__file__).parent / "rubric.json"
    with open(rubric_path, 'r', encoding='utf-8') as f:
        rubric_data = json.load(f)

    # Load answer
    text = find_answer_file(args.submission)
    if not text:
        print("No answer file found")
        print("score=0.00")
        print("result=FAILED")
        return

    print(f"Answer: {len(text)} characters\n")

    # Part 1: Numerical checks
    num_checks = rubric_data.get("numerical_checks", [])
    if num_checks:
        print("=== Numerical Verification ===")
        num_result = check_numerical(text, num_checks)
        for d in num_result["details"]:
            print(d)
        print(f"Numerical score: {num_result['score']:.2%}\n")
    else:
        num_result = {"score": 0}

    # Part 2: Rubric checks
    rub_checks = rubric_data.get("rubric_checks", [])
    if rub_checks:
        print("=== Rubric Evaluation ===")
        rub_result = check_rubric(text, rubric_data.get("question", ""), rub_checks)
        for d in rub_result["details"]:
            print(d)
        print(f"Rubric score: {rub_result['score']:.2%}\n")
    else:
        rub_result = {"score": 0}

    # Combined score
    if num_checks and rub_checks:
        final_score = NUMERICAL_WEIGHT * num_result["score"] + RUBRIC_WEIGHT * rub_result["score"]
    elif num_checks:
        final_score = num_result["score"]
    else:
        final_score = rub_result["score"]

    passed = final_score >= PASS_THRESHOLD
    print(f"{'='*50}")
    print(f"Final score: {final_score:.2%}")
    print(f"score={final_score:.2f}")
    print(f"result={'PASSED' if passed else 'FAILED'}")


if __name__ == "__main__":
    main()

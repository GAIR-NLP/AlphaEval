#!/usr/bin/env python3
"""
LLM-as-Judge Evaluation Template — Rubric-based Assessment

Use this template when the agent's output requires subjective quality assessment.
The script loads rubric points from rubric.json and uses an LLM to judge each point.

Each rubric point is evaluated independently:
    - "covered" if the agent's output addresses the criterion
    - "not covered" if not

Final score = weighted coverage rate (0.0 to 1.0)

Output format (required):
    score=X.XX    (0.00 to 1.00)
    result=PASSED or result=FAILED
"""

import os
import sys
import json
import argparse
import yaml

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)


# ============================================================
# CONFIGURATION
# ============================================================

PASS_THRESHOLD = 0.6   # Minimum coverage rate to pass
MAX_ANSWER_LENGTH = 30000  # Truncate long answers for the judge


# ============================================================
# CONFIG LOADING
# ============================================================

def load_config():
    """Load API config from config.yaml."""
    config_paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "config.yaml"),
        os.path.join(os.getcwd(), "config.yaml"),
    ]
    for config_path in config_paths:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    return {}


def find_answer_file(workspace_dir: str) -> str:
    """Find the agent's answer file."""
    for base in [workspace_dir, os.path.join(workspace_dir, "..")]:
        ans_path = os.path.join(base, "results", "ans.md")
        if os.path.exists(ans_path):
            with open(ans_path, 'r', encoding='utf-8') as f:
                return f.read()
    return None


# ============================================================
# LLM JUDGE — Per-rubric-point evaluation
# ============================================================

def get_evaluation_prompt(question, rubric_point, weight, ai_response):
    """Build the evaluation prompt for a single rubric point."""
    return f"""# Rubric Evaluation

## Task
Judge whether the AI's response adequately covers the specified criterion.
Answer "yes" or "no", then give a brief reason.

## Research Question
{question}

## Criterion (weight={weight})
{rubric_point}

## AI Response (truncated)
{ai_response[:MAX_ANSWER_LENGTH]}

## Your Judgment
First line: "yes" or "no"
Second line: brief reason (1-2 sentences)
"""


class RubricEvaluator:
    def __init__(self, judge_model="gpt-4o"):
        config = load_config()
        llm_config = config.get("llm", {})
        self.client = OpenAI(
            api_key=llm_config.get("api_key", os.environ.get("OPENAI_API_KEY", "")),
            base_url=llm_config.get("base_url", "https://api.openai.com/v1"),
        )
        self.model = llm_config.get("judge_model", judge_model)

    def evaluate_single_rubric(self, question, rubric_point, weight, ai_response):
        """Judge a single rubric point. Returns (is_covered: bool, reason: str)."""
        prompt = get_evaluation_prompt(question, rubric_point, weight, ai_response)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an evaluation assistant. Judge strictly based on evidence in the response."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.0,
            )
            result = response.choices[0].message.content.strip()
            first_line = result.split('\n')[0].lower().strip()
            if first_line.startswith('yes'):
                return True, result
            else:
                return False, result
        except Exception as e:
            return False, f"API error: {str(e)}"

    def evaluate(self, question, rubrics, ai_response):
        """Evaluate all rubric points. Returns coverage dict."""
        total_weight = 0
        covered_weight = 0
        print(f"Evaluating {len(rubrics)} rubric points...")

        for i, rubric in enumerate(rubrics):
            point = rubric["point"]
            weight = rubric.get("weight", 1)
            total_weight += weight

            is_covered, reason = self.evaluate_single_rubric(question, point, weight, ai_response)
            if is_covered:
                covered_weight += weight
                print(f"  [PASS] Point {i+1}/{len(rubrics)} (weight={weight})")
            else:
                print(f"  [FAIL] Point {i+1}/{len(rubrics)} (weight={weight}): {reason[:100]}")

        coverage = covered_weight / total_weight if total_weight > 0 else 0
        return {"total_weight": total_weight, "covered_weight": covered_weight, "coverage": round(coverage, 4)}


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", required=True, help="Submission directory")
    args = parser.parse_args()

    # Load rubric
    rubric_path = os.path.join(os.path.dirname(__file__), "rubric.json")
    with open(rubric_path, 'r', encoding='utf-8') as f:
        rubric_data = json.load(f)

    question = rubric_data["question"]
    rubrics = rubric_data["rubrics"]

    # Load agent answer
    ai_response = find_answer_file(args.submission)
    if not ai_response:
        print("No answer file found at results/ans.md")
        print("score=0.00")
        print("result=FAILED")
        return

    print(f"Answer found: {len(ai_response)} characters")

    # Evaluate
    evaluator = RubricEvaluator()
    result = evaluator.evaluate(question, rubrics, ai_response)

    passed = result["coverage"] >= PASS_THRESHOLD
    print(f"\n{'='*50}")
    print(f"Coverage: {result['coverage']:.2%} ({result['covered_weight']}/{result['total_weight']})")
    print(f"score={result['coverage']:.2f}")
    print(f"result={'PASSED' if passed else 'FAILED'}")


if __name__ == "__main__":
    main()

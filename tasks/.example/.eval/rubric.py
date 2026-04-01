#!/usr/bin/env python3
"""Example rubric evaluation script.

This script evaluates the agent's output against predefined criteria.
It should print:
  score=X.XX  (0.00 to 1.00)
  result=PASSED or result=FAILED
"""

import argparse
import os


def find_answer_file(workspace_dir: str) -> str:
    """Find the agent's answer file."""
    ans_path = os.path.join(workspace_dir, "results", "ans.md")
    if os.path.exists(ans_path):
        with open(ans_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def evaluate(answer: str) -> dict:
    """Evaluate the answer against rubric criteria.

    Returns:
        dict with 'score' (float 0-1) and 'passed' (bool)
    """
    # TODO: Implement your evaluation logic here
    # Example: check if answer contains required keywords
    score = 0.0

    # Add your rubric checks here
    # criteria = [
    #     ("criterion_1", weight_1, check_function_1),
    #     ("criterion_2", weight_2, check_function_2),
    # ]

    passed = score >= 0.6
    return {"score": score, "passed": passed}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", required=True, help="Submission directory")
    args = parser.parse_args()

    answer = find_answer_file(args.submission)
    if not answer:
        print("No answer file found")
        print("score=0.00")
        print("result=FAILED")
        return

    result = evaluate(answer)
    print(f"score={result['score']:.2f}")
    print(f"result={'PASSED' if result['passed'] else 'FAILED'}")


if __name__ == "__main__":
    main()

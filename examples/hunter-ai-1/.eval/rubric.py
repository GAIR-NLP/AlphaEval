#!/usr/bin/env python3
"""
Resume Screening Evaluation — F1 Score

Compares the agent's candidate selections against actual hiring decisions.
Uses F1 score (precision × recall harmonic mean) as the primary metric.
"""

import re
import json
import argparse
from pathlib import Path
from typing import Set

PASS_THRESHOLD = 0.6


def parse_selected_candidates(text: str) -> Set[str]:
    """Extract candidate IDs from agent output."""
    candidates = set()

    # Match patterns like "candidate_XX", "Candidate XX"
    for match in re.finditer(r'candidate[_\s-]*(\d+)', text, re.IGNORECASE):
        candidates.add(f"candidate_{match.group(1).zfill(2)}")

    # Also try alternative patterns
    for match in re.finditer(r'Candidate[_\s-]*(\d+)', text):
        candidates.add(f"candidate_{match.group(1).zfill(2)}")

    # Try just numbered list with names
    if not candidates:
        for match in re.finditer(r'^\s*\d+[\.\)]\s*(\S+)', text, re.MULTILINE):
            name = match.group(1).strip()
            num = re.search(r'(\d+)', name)
            if num:
                candidates.add(f"candidate_{num.group(1).zfill(2)}")

    return candidates


def compute_f1(predicted: Set[str], ground_truth: Set[str]) -> dict:
    tp = len(predicted & ground_truth)
    fp = len(predicted - ground_truth)
    fn = len(ground_truth - predicted)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", required=True)
    args = parser.parse_args()

    # Load ground truth
    gt_path = Path(__file__).parent / "ground_truth.json"
    with open(gt_path, 'r') as f:
        gt_data = json.load(f)
    ground_truth = set(gt_data["correct_candidates"])

    # Load answer
    ans_path = Path(args.submission) / "results" / "ans.md"
    if not ans_path.exists():
        ans_path = Path(args.submission).parent / "results" / "ans.md"

    if not ans_path.exists():
        print("No answer file found")
        print("score=0.00")
        print("result=FAILED")
        return

    text = ans_path.read_text(encoding='utf-8')
    predicted = parse_selected_candidates(text)
    metrics = compute_f1(predicted, ground_truth)

    print(f"Ground truth: {sorted(ground_truth)}")
    print(f"Predicted: {sorted(predicted)}")
    print(f"TP={metrics['tp']}, FP={metrics['fp']}, FN={metrics['fn']}")
    print(f"Precision={metrics['precision']:.2%}, Recall={metrics['recall']:.2%}, F1={metrics['f1']:.2%}")
    print(f"score={metrics['f1']:.2f}")
    print(f"result={'PASSED' if metrics['f1'] >= PASS_THRESHOLD else 'FAILED'}")


if __name__ == "__main__":
    main()

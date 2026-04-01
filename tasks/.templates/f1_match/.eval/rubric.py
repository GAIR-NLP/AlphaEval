#!/usr/bin/env python3
"""
F1 Score Evaluation Template — Set Matching

Use this template when the agent must select a subset of items from a collection.
Computes Precision, Recall, and F1 against ground truth selections.

Output format (required):
    score=X.XX    (F1 score, 0.00 to 1.00)
    result=PASSED or result=FAILED
"""

import re
import json
import argparse
from pathlib import Path
from typing import List, Set


# ============================================================
# CONFIGURATION
# ============================================================

PASS_THRESHOLD = 0.6     # Minimum F1 to pass


# ============================================================
# ANSWER PARSING
# ============================================================

def parse_selected_items(text: str) -> Set[str]:
    """Extract selected item names/IDs from agent output.

    Customize the parsing logic to match your expected output format.
    """
    items = set()

    # Pattern 1: numbered list "1. item_name"
    for match in re.finditer(r'^\s*\d+[\.\)]\s*(.+?)(?:\s*[-—].*)?$', text, re.MULTILINE):
        item = match.group(1).strip()
        item = re.sub(r'\s*[（(].*$', '', item)  # Remove parenthetical notes
        if item:
            items.add(normalize_item(item))

    # Pattern 2: bullet list "- item_name" or "• item_name"
    if not items:
        for match in re.finditer(r'^\s*[-•*]\s*(.+?)(?:\s*[-—].*)?$', text, re.MULTILINE):
            item = match.group(1).strip()
            if item:
                items.add(normalize_item(item))

    return items


def normalize_item(name: str) -> str:
    """Normalize item name for comparison.

    Customize based on your item naming convention.
    """
    name = name.strip().lower()
    name = re.sub(r'[_\-\s]+', '_', name)
    name = re.sub(r'\.pdf$|\.docx?$|\.txt$', '', name)
    return name


# ============================================================
# F1 COMPUTATION
# ============================================================

def compute_f1(predicted: Set[str], ground_truth: Set[str]) -> dict:
    """Compute precision, recall, and F1 score."""
    if not predicted and not ground_truth:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "tp": 0, "fp": 0, "fn": 0}

    tp = len(predicted & ground_truth)
    fp = len(predicted - ground_truth)
    fn = len(ground_truth - predicted)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp, "fp": fp, "fn": fn,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", required=True, help="Submission directory")
    args = parser.parse_args()

    # Load ground truth
    gt_path = Path(__file__).parent / "ground_truth.json"
    with open(gt_path, 'r', encoding='utf-8') as f:
        gt_data = json.load(f)
    ground_truth = {normalize_item(item) for item in gt_data["correct_items"]}

    # Load agent answer
    ans_path = Path(args.submission) / "results" / "ans.md"
    if not ans_path.exists():
        ans_path = Path(args.submission).parent / "results" / "ans.md"

    if not ans_path.exists():
        print("No answer file found")
        print("score=0.00")
        print("result=FAILED")
        return

    text = ans_path.read_text(encoding='utf-8')
    predicted = parse_selected_items(text)

    # Compute metrics
    metrics = compute_f1(predicted, ground_truth)
    passed = metrics["f1"] >= PASS_THRESHOLD

    print(f"Ground truth: {len(ground_truth)} items")
    print(f"Predicted: {len(predicted)} items")
    print(f"TP={metrics['tp']}, FP={metrics['fp']}, FN={metrics['fn']}")
    print(f"Precision={metrics['precision']:.2%}, Recall={metrics['recall']:.2%}")
    print(f"F1={metrics['f1']:.2%}")
    print(f"score={metrics['f1']:.2f}")
    print(f"result={'PASSED' if passed else 'FAILED'}")


if __name__ == "__main__":
    main()

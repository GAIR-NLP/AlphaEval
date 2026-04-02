#!/usr/bin/env python3
"""Aircraft delivery analysis — LLM-as-Judge rubric evaluation (fictional example).

Evaluates the agent's analysis report against rubric points defined in rubric.json.
Each point is checked by an LLM judge for coverage in the agent's output.
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


def load_config():
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
    for base in [workspace_dir, os.path.join(workspace_dir, "..")]:
        ans_path = os.path.join(base, "results", "ans.md")
        if os.path.exists(ans_path):
            with open(ans_path, 'r', encoding='utf-8') as f:
                return f.read()
    return None


class RubricEvaluator:
    def __init__(self, judge_model="gpt-4o"):
        config = load_config()
        llm_config = config.get("llm", {})
        self.client = OpenAI(
            api_key=llm_config.get("api_key", os.environ.get("OPENAI_API_KEY", "")),
            base_url=llm_config.get("base_url", "https://api.openai.com/v1"),
        )
        self.model = llm_config.get("judge_model", judge_model)

    def evaluate_single(self, question, point, weight, response):
        prompt = f"""Judge whether this AI response covers the criterion. Answer "yes" or "no".

Question: {question}
Criterion: {point}
Response (truncated): {response[:30000]}

First line: yes or no
Second line: brief reason"""
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200, temperature=0.0,
            )
            text = resp.choices[0].message.content.strip()
            return text.split('\n')[0].lower().startswith('yes'), text
        except Exception as e:
            return False, str(e)

    def evaluate(self, question, rubrics, response):
        total_w = covered_w = 0
        for i, r in enumerate(rubrics):
            w = r.get("weight", 1)
            total_w += w
            ok, reason = self.evaluate_single(question, r["point"], w, response)
            if ok:
                covered_w += w
                print(f"  [PASS] {i+1}/{len(rubrics)} (w={w})")
            else:
                print(f"  [FAIL] {i+1}/{len(rubrics)} (w={w})")
        return covered_w / total_w if total_w > 0 else 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", required=True)
    args = parser.parse_args()

    rubric_path = os.path.join(os.path.dirname(__file__), "rubric.json")
    with open(rubric_path, 'r') as f:
        data = json.load(f)

    response = find_answer_file(args.submission)
    if not response:
        print("No answer file found")
        print("score=0.00")
        print("result=FAILED")
        return

    print(f"Answer: {len(response)} chars, {len(data['rubrics'])} rubric points")
    evaluator = RubricEvaluator()
    score = evaluator.evaluate(data["question"], data["rubrics"], response)

    print(f"\nscore={score:.2f}")
    print(f"result={'PASSED' if score >= 0.6 else 'FAILED'}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Parallel meta-evaluation: two Opus annotators judge rubric coverage concurrently."""

import json
import os
import sys
import time
import yaml
import concurrent.futures
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("pip install openai first")
    sys.exit(1)

BASE_DIR = Path("/data2/prlu/agent_eval")
TASKS_DIR = BASE_DIR / "tasks"
FINAL_DIR = BASE_DIR / "final"
OUTPUT_DIR = BASE_DIR / "meta_eval_results"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_config():
    config_path = BASE_DIR / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}

config = load_config()
llm_config = config.get("llm", {})

ANNOTATOR_PROMPTS = {
    "A": "You are Annotator A, a strict and precise evaluator. You only mark a rubric point as covered if the response explicitly and clearly addresses the criterion with specific evidence. When in doubt, mark as NOT covered.",
    "B": "You are Annotator B, a thorough but fair evaluator. You mark a rubric point as covered if the response substantially addresses the criterion, even if not using the exact same terminology. Give reasonable credit for paraphrased or implicit coverage.",
}

def get_client():
    api_key = llm_config.get("api_key", os.environ.get("OPENAI_API_KEY", ""))
    base_url = llm_config.get("base_url", "https://api.openai.com/v1")
    return OpenAI(api_key=api_key, base_url=base_url)

def judge_single(args):
    """Judge a single (annotator, rubric_point) pair. Used for parallel execution."""
    client, annotator_id, question, point, weight, ai_response, model = args
    system_prompt = ANNOTATOR_PROMPTS[annotator_id]
    user_prompt = f"""# Rubric Evaluation Task

## Your Role
{system_prompt}

## Research Question
{question}

## Rubric Criterion (Weight={weight})
{point}

## AI Research Response (truncated to 30000 chars)
{ai_response[:30000]}

## Instructions
Does the AI response adequately cover this rubric criterion?
Reply with EXACTLY one of:
- "COVERED" if the criterion is met
- "NOT_COVERED" if the criterion is not met

Then on the next line, provide a brief justification (1-2 sentences).
"""
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=200,
                temperature=0.0,
            )
            text = resp.choices[0].message.content.strip()
            first_line = text.split("\n")[0].upper()
            covered = "COVERED" in first_line and "NOT_COVERED" not in first_line
            return {"annotator": annotator_id, "covered": covered, "raw_response": text}
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                return {"annotator": annotator_id, "covered": None, "raw_response": str(e)}


def evaluate_task(client, cfg_name, task_id, model, max_workers=10):
    """Evaluate all rubric points for one task with both annotators in parallel."""
    ans_path = FINAL_DIR / cfg_name / task_id / "ans.md"
    rubric_path = TASKS_DIR / task_id / ".eval" / "rubric.json"

    if not ans_path.exists():
        return None

    with open(rubric_path) as f:
        rubric_data = json.load(f)
    with open(ans_path) as f:
        ai_response = f.read()

    if not ai_response.strip():
        return None

    question = rubric_data["question"]
    rubrics = rubric_data["rubrics"]

    # Build all jobs: 2 annotators × N rubric points
    jobs = []
    for i, rubric in enumerate(rubrics):
        for ann_id in ["A", "B"]:
            jobs.append((client, ann_id, question, rubric["point"], rubric.get("weight", 1), ai_response, model))

    # Execute in parallel
    results_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(judge_single, job): (i // 2, job[1]) for i, job in enumerate(jobs)}
        for future in concurrent.futures.as_completed(futures):
            point_idx, ann_id = futures[future]
            result = future.result()
            results_map[(point_idx, ann_id)] = result

    # Organize results
    task_result = {
        "config": cfg_name,
        "task_id": task_id,
        "num_rubric_points": len(rubrics),
        "annotator_A": [],
        "annotator_B": [],
    }

    for i, rubric in enumerate(rubrics):
        for ann_id in ["A", "B"]:
            r = results_map.get((i, ann_id), {"covered": None, "raw_response": "missing"})
            entry = {
                "point_idx": i,
                "point": rubric["point"],
                "weight": rubric.get("weight", 1),
                "covered": r["covered"],
                "reasoning": r["raw_response"],
            }
            task_result[f"annotator_{ann_id}"].append(entry)

    return task_result


def compute_metrics(results):
    """Compute agreement metrics."""
    agree_count = 0
    total_count = 0
    a_covered = 0
    b_covered = 0
    both_covered = 0
    neither_covered = 0
    task_scores = {}

    for task_result in results:
        cfg = task_result["config"]
        tid = task_result["task_id"]
        key = f"{cfg}/{tid}"
        a_results = task_result["annotator_A"]
        b_results = task_result["annotator_B"]
        a_score = 0
        b_score = 0
        total_weight = 0

        for a, b in zip(a_results, b_results):
            if a["covered"] is None or b["covered"] is None:
                continue
            total_count += 1
            if a["covered"] == b["covered"]:
                agree_count += 1
            if a["covered"]:
                a_covered += 1
            if b["covered"]:
                b_covered += 1
            if a["covered"] and b["covered"]:
                both_covered += 1
            if not a["covered"] and not b["covered"]:
                neither_covered += 1
            if a["covered"]:
                a_score += a["weight"]
            if b["covered"]:
                b_score += b["weight"]
            total_weight += a["weight"]

        if total_weight > 0:
            task_scores[key] = {
                "annotator_A_score": round(a_score / total_weight, 4),
                "annotator_B_score": round(b_score / total_weight, 4),
                "avg_score": round((a_score + b_score) / (2 * total_weight), 4),
            }

    if total_count > 0:
        po = agree_count / total_count
        pa = a_covered / total_count
        pb = b_covered / total_count
        pe = pa * pb + (1 - pa) * (1 - pb)
        kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0

        # Confusion matrix
        tp = both_covered
        tn = neither_covered
        fp = a_covered - both_covered  # A says yes, B says no
        fn = b_covered - both_covered  # B says yes, A says no
    else:
        po = kappa = 0
        tp = tn = fp = fn = 0

    # Spearman correlation on task-level scores
    if len(task_scores) >= 3:
        from scipy import stats
        a_scores = [v["annotator_A_score"] for v in task_scores.values()]
        b_scores = [v["annotator_B_score"] for v in task_scores.values()]
        try:
            spearman, sp_pval = stats.spearmanr(a_scores, b_scores)
            pearson, pe_pval = stats.pearsonr(a_scores, b_scores)
        except:
            spearman = pearson = sp_pval = pe_pval = None
    else:
        spearman = pearson = sp_pval = pe_pval = None

    return {
        "total_judgments": total_count,
        "inter_annotator_agreement": round(po, 4),
        "cohens_kappa": round(kappa, 4),
        "annotator_A_coverage_rate": round(a_covered / total_count, 4) if total_count > 0 else 0,
        "annotator_B_coverage_rate": round(b_covered / total_count, 4) if total_count > 0 else 0,
        "confusion_matrix": {"TP": tp, "TN": tn, "FP_A_yes_B_no": fp, "FN_A_no_B_yes": fn},
        "spearman_correlation": round(spearman, 4) if spearman is not None else None,
        "spearman_pvalue": round(sp_pval, 6) if sp_pval is not None else None,
        "pearson_correlation": round(pearson, 4) if pearson is not None else None,
        "pearson_pvalue": round(pe_pval, 6) if pe_pval is not None else None,
        "task_scores": task_scores,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", nargs="+", default=[
        "cc_opus", "codex_gpt5.2", "cursor_opus", "cc_glm5", "copilot_gemini3"
    ])
    parser.add_argument("--tasks", type=str, default="1-10")
    parser.add_argument("--model", default="claude-opus-4-6")
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()

    start, end = map(int, args.tasks.split("-"))
    task_range = range(start, end + 1)

    client = get_client()
    all_results = []
    total_tasks = len(args.configs) * len(task_range)
    completed = 0

    print(f"Meta-evaluation: {len(args.configs)} configs × {len(task_range)} tasks = {total_tasks} evaluations")
    print(f"Judge model: {args.model}, Workers: {args.workers}")

    for cfg_name in args.configs:
        for task_idx in task_range:
            task_id = f"jiqizhixin-{task_idx}"
            completed += 1
            print(f"\n[{completed}/{total_tasks}] {cfg_name} / {task_id}", flush=True)

            result = evaluate_task(client, cfg_name, task_id, args.model, args.workers)
            if result:
                all_results.append(result)
                # Count covered
                a_cov = sum(1 for r in result["annotator_A"] if r["covered"])
                b_cov = sum(1 for r in result["annotator_B"] if r["covered"])
                print(f"  A: {a_cov}/20 covered, B: {b_cov}/20 covered", flush=True)

                # Save incrementally
                with open(OUTPUT_DIR / "meta_eval_raw.json", "w") as f:
                    json.dump(all_results, f, ensure_ascii=False, indent=2)
            else:
                print(f"  Skipped (no output)", flush=True)

    metrics = compute_metrics(all_results)
    with open(OUTPUT_DIR / "meta_eval_metrics.json", "w") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print("META-EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"Total judgments: {metrics['total_judgments']}")
    print(f"Inter-annotator agreement: {metrics['inter_annotator_agreement']:.2%}")
    print(f"Cohen's Kappa: {metrics['cohens_kappa']:.4f}")
    print(f"Annotator A coverage rate: {metrics['annotator_A_coverage_rate']:.2%}")
    print(f"Annotator B coverage rate: {metrics['annotator_B_coverage_rate']:.2%}")
    print(f"Confusion matrix: {metrics['confusion_matrix']}")
    if metrics['spearman_correlation'] is not None:
        print(f"Spearman correlation: {metrics['spearman_correlation']:.4f} (p={metrics['spearman_pvalue']})")
        print(f"Pearson correlation: {metrics['pearson_correlation']:.4f} (p={metrics['pearson_pvalue']})")
    print(f"\nResults saved to: {OUTPUT_DIR}")

#!/usr/bin/env python3
"""Meta-evaluation: compare Annotator A, Annotator B, and automated LLM-as-Judge."""

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

# Three evaluators: two Opus annotators + the automated judge
EVALUATOR_PROMPTS = {
    "A": "You are Annotator A, a strict and precise evaluator. You only mark a rubric point as covered if the response explicitly and clearly addresses the criterion with specific evidence. When in doubt, mark as NOT covered.",
    "B": "You are Annotator B, a thorough but fair evaluator. You mark a rubric point as covered if the response substantially addresses the criterion, even if not using the exact same terminology. Give reasonable credit for paraphrased or implicit coverage.",
    "Auto": "你是一个深度调研评分助手。请严格根据评分标准判断AI的回答是否包含了指定的关键信息。",
}

def get_client():
    api_key = llm_config.get("api_key", os.environ.get("OPENAI_API_KEY", ""))
    base_url = llm_config.get("base_url", "https://api.openai.com/v1")
    return OpenAI(api_key=api_key, base_url=base_url)

def judge_single(args):
    """Judge a single rubric point."""
    client, evaluator_id, question, point, weight, ai_response, model = args

    if evaluator_id == "Auto":
        # Use the same prompt format as rubric.py for the automated judge
        user_prompt = f"""# Deep Research Rubric Evaluation

## Task
判断 AI 的深度调研回答是否包含了指定评分点中的关键信息。回答 "yes" 或 "no"，并给出简短理由。

## Input Materials
<Research Question>: {question}
<Criterion>: {point}
<Weight>: {weight}
<AI Research Response>:
{ai_response[:30000]}

## Evaluation Instructions
- 仔细阅读AI的回答
- 判断是否包含了评分点要求的关键信息
- 回答格式：第一行写 "yes" 或 "no"，第二行写理由

## Your Evaluation:"""
        system_prompt = EVALUATOR_PROMPTS["Auto"]
    else:
        system_prompt = EVALUATOR_PROMPTS[evaluator_id]
        user_prompt = f"""# Rubric Evaluation Task

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
            if evaluator_id == "Auto":
                covered = first_line.startswith("YES")
            else:
                covered = "COVERED" in first_line and "NOT_COVERED" not in first_line
            return {"evaluator": evaluator_id, "covered": covered, "raw_response": text}
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                return {"evaluator": evaluator_id, "covered": None, "raw_response": str(e)}


def evaluate_task(client, cfg_name, task_id, opus_model, auto_model, max_workers=15):
    """Evaluate all rubric points with A, B (Opus), and Auto (Sonnet) in parallel."""
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

    # Build jobs: 3 evaluators × N rubric points
    jobs = []
    job_keys = []
    for i, rubric in enumerate(rubrics):
        for eval_id in ["A", "B", "Auto"]:
            model = opus_model if eval_id in ["A", "B"] else auto_model
            jobs.append((client, eval_id, question, rubric["point"], rubric.get("weight", 1), ai_response, model))
            job_keys.append((i, eval_id))

    results_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(judge_single, job): key for job, key in zip(jobs, job_keys)}
        for future in concurrent.futures.as_completed(futures):
            key = futures[future]
            results_map[key] = future.result()

    task_result = {
        "config": cfg_name,
        "task_id": task_id,
        "num_rubric_points": len(rubrics),
        "annotator_A": [],
        "annotator_B": [],
        "auto_judge": [],
    }

    for i, rubric in enumerate(rubrics):
        for eval_id, key in [("A", "annotator_A"), ("B", "annotator_B"), ("Auto", "auto_judge")]:
            r = results_map.get((i, eval_id), {"covered": None, "raw_response": "missing"})
            task_result[key].append({
                "point_idx": i,
                "point": rubric["point"],
                "weight": rubric.get("weight", 1),
                "covered": r["covered"],
                "reasoning": r["raw_response"],
            })

    return task_result


def compute_pairwise(results, key1, key2):
    """Compute agreement between two evaluators."""
    agree = total = e1_yes = e2_yes = both_yes = both_no = 0

    task_scores_1 = {}
    task_scores_2 = {}

    for r in results:
        cfg_task = f"{r['config']}/{r['task_id']}"
        s1 = s2 = tw = 0
        for a, b in zip(r[key1], r[key2]):
            if a["covered"] is None or b["covered"] is None:
                continue
            total += 1
            if a["covered"] == b["covered"]:
                agree += 1
            if a["covered"]:
                e1_yes += 1
                s1 += a["weight"]
            if b["covered"]:
                e2_yes += 1
                s2 += b["weight"]
            if a["covered"] and b["covered"]:
                both_yes += 1
            if not a["covered"] and not b["covered"]:
                both_no += 1
            tw += a["weight"]
        if tw > 0:
            task_scores_1[cfg_task] = s1 / tw
            task_scores_2[cfg_task] = s2 / tw

    if total == 0:
        return {"agreement": 0, "kappa": 0, "spearman": None, "pearson": None}

    po = agree / total
    p1 = e1_yes / total
    p2 = e2_yes / total
    pe = p1 * p2 + (1 - p1) * (1 - p2)
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0

    spearman = pearson = sp_p = pe_p = None
    if len(task_scores_1) >= 3:
        from scipy import stats
        s1_list = [task_scores_1[k] for k in sorted(task_scores_1)]
        s2_list = [task_scores_2[k] for k in sorted(task_scores_2)]
        try:
            spearman, sp_p = stats.spearmanr(s1_list, s2_list)
            pearson, pe_p = stats.pearsonr(s1_list, s2_list)
        except:
            pass

    return {
        "total_judgments": total,
        "agreement": round(po, 4),
        "cohens_kappa": round(kappa, 4),
        "e1_coverage_rate": round(e1_yes / total, 4),
        "e2_coverage_rate": round(e2_yes / total, 4),
        "confusion": {"TP": both_yes, "TN": both_no, "FP": e1_yes - both_yes, "FN": e2_yes - both_yes},
        "spearman": round(spearman, 4) if spearman is not None else None,
        "spearman_p": round(sp_p, 6) if sp_p is not None else None,
        "pearson": round(pearson, 4) if pearson is not None else None,
        "pearson_p": round(pe_p, 6) if pe_p is not None else None,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", nargs="+", default=[
        "cc_opus", "codex_gpt5.2", "cursor_opus", "cc_glm5", "copilot_gemini3"
    ])
    parser.add_argument("--tasks", type=str, default="1-10")
    parser.add_argument("--opus-model", default="claude-opus-4-6")
    parser.add_argument("--auto-model", default="claude-sonnet-4-6")
    parser.add_argument("--workers", type=int, default=15)
    args = parser.parse_args()

    start, end = map(int, args.tasks.split("-"))
    task_range = range(start, end + 1)

    client = get_client()

    # Load existing A/B results if available
    existing_path = OUTPUT_DIR / "meta_eval_raw.json"
    existing_ab = {}
    if existing_path.exists():
        with open(existing_path) as f:
            for r in json.load(f):
                existing_ab[f"{r['config']}/{r['task_id']}"] = r

    all_results = []
    total_tasks = len(args.configs) * len(task_range)
    completed = 0

    print(f"Meta-evaluation with Auto judge: {len(args.configs)} configs × {len(task_range)} tasks = {total_tasks}")
    print(f"Opus model: {args.opus_model}, Auto model: {args.auto_model}, Workers: {args.workers}")

    for cfg_name in args.configs:
        for task_idx in task_range:
            task_id = f"jiqizhixin-{task_idx}"
            completed += 1
            key = f"{cfg_name}/{task_id}"

            # If we have existing A/B results, only run Auto
            if key in existing_ab:
                print(f"[{completed}/{total_tasks}] {key} — reusing A/B, running Auto only", flush=True)

                # Run Auto judge only
                ans_path = FINAL_DIR / cfg_name / task_id / "ans.md"
                rubric_path = TASKS_DIR / task_id / ".eval" / "rubric.json"
                if not ans_path.exists():
                    print(f"  Skipped", flush=True)
                    continue
                with open(rubric_path) as f:
                    rubric_data = json.load(f)
                with open(ans_path) as f:
                    ai_response = f.read()
                if not ai_response.strip():
                    continue

                question = rubric_data["question"]
                rubrics = rubric_data["rubrics"]

                auto_jobs = []
                for i, rubric in enumerate(rubrics):
                    auto_jobs.append((client, "Auto", question, rubric["point"], rubric.get("weight", 1), ai_response, args.auto_model))

                auto_results = {}
                with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
                    futures = {executor.submit(judge_single, job): i for i, job in enumerate(auto_jobs)}
                    for future in concurrent.futures.as_completed(futures):
                        idx = futures[future]
                        auto_results[idx] = future.result()

                result = dict(existing_ab[key])
                result["auto_judge"] = []
                for i, rubric in enumerate(rubrics):
                    r = auto_results.get(i, {"covered": None, "raw_response": "missing"})
                    result["auto_judge"].append({
                        "point_idx": i,
                        "point": rubric["point"],
                        "weight": rubric.get("weight", 1),
                        "covered": r["covered"],
                        "reasoning": r["raw_response"],
                    })

                a_cov = sum(1 for r in result["annotator_A"] if r["covered"])
                b_cov = sum(1 for r in result["annotator_B"] if r["covered"])
                auto_cov = sum(1 for r in result["auto_judge"] if r["covered"])
                print(f"  A:{a_cov}/20  B:{b_cov}/20  Auto:{auto_cov}/20", flush=True)
                all_results.append(result)
            else:
                print(f"[{completed}/{total_tasks}] {key} — running all three", flush=True)
                result = evaluate_task(client, cfg_name, task_id, args.opus_model, args.auto_model, args.workers)
                if result:
                    a_cov = sum(1 for r in result["annotator_A"] if r["covered"])
                    b_cov = sum(1 for r in result["annotator_B"] if r["covered"])
                    auto_cov = sum(1 for r in result["auto_judge"] if r["covered"])
                    print(f"  A:{a_cov}/20  B:{b_cov}/20  Auto:{auto_cov}/20", flush=True)
                    all_results.append(result)

            # Save incrementally
            with open(OUTPUT_DIR / "meta_eval_full.json", "w") as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)

    # Compute all three pairs
    print(f"\n{'='*60}")
    print("PAIRWISE AGREEMENT METRICS")
    print(f"{'='*60}")

    pairs = [
        ("A vs B", "annotator_A", "annotator_B"),
        ("A vs Auto", "annotator_A", "auto_judge"),
        ("B vs Auto", "annotator_B", "auto_judge"),
    ]

    all_metrics = {}
    for label, k1, k2 in pairs:
        m = compute_pairwise(all_results, k1, k2)
        all_metrics[label] = m
        print(f"\n{label}:")
        print(f"  Agreement: {m['agreement']:.2%}")
        print(f"  Cohen's κ: {m['cohens_kappa']:.4f}")
        print(f"  Spearman ρ: {m['spearman']}")
        print(f"  Pearson r: {m['pearson']}")

    with open(OUTPUT_DIR / "meta_eval_full_metrics.json", "w") as f:
        json.dump(all_metrics, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved to: {OUTPUT_DIR}")

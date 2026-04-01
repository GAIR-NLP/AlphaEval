# Task Creation Guide

## Overview

Each task is a self-contained directory with a standardized structure. Choose the evaluation template that best fits your task, then customize it.

## Evaluation Templates

| Template | When to Use | Example Tasks |
|----------|------------|---------------|
| `code_exec` | Answer has verifiable numeric/structured output | BOM optimization, data extraction, calculation |
| `llm_judge` | Answer requires subjective quality assessment | Research reports, analytical writing, policy analysis |
| `exact_match` | Answer is a single correct value | Math problems, factual Q&A, classification |
| `f1_match` | Agent must select items from a set | Resume screening, document selection, entity extraction |
| `hybrid` | Needs BOTH numeric accuracy AND qualitative quality | Clinical calculations + reasoning, financial analysis + insights |

## Quick Start

### Step 1: Copy a template

```bash
cp -r tasks/.templates/llm_judge tasks/my-new-task
```

### Step 2: Edit task.yaml

```yaml
name: "My New Task"
description: "What the agent needs to do"
category: finance          # hr, finance, procurement, software, healthcare, research
difficulty: hard
```

### Step 3: Write query.md

This is the prompt the agent sees. Be as specific (or as ambiguous) as your real production requirement.

### Step 4: Add input files

Place any PDFs, Excel files, images, or other input data in `files/`.

### Step 5: Configure evaluation

Choose your approach:

#### For `code_exec` (Constraint Verification):
Edit `.eval/rubric.py`:
- Set `EXPECTED_VALUE` to the correct answer
- Customize `extract_answer()` to parse the agent's output format

#### For `llm_judge` (Rubric-based):
Edit `.eval/rubric.json`:
```json
{
    "question": "The main task question",
    "rubrics": [
        {"point": "Criterion 1 — what must be in the answer", "weight": 2},
        {"point": "Criterion 2 — another required element", "weight": 1}
    ]
}
```
Tips:
- Weight 1 = nice to have, Weight 2 = important, Weight 3 = essential
- Be specific: "Mentioned Harvey AI's $160M F-round" not "Discussed funding"
- Aim for 10-20 rubric points per task

#### For `exact_match`:
Edit `.eval/rubric.py`:
- Set `EXPECTED_ANSWER`
- Set `NUMERIC_MODE = True/False`

#### For `f1_match` (Set Matching):
Edit `.eval/ground_truth.json`:
```json
{
    "correct_items": ["item_1", "item_5", "item_12"],
    "notes": "Confirmed by domain expert"
}
```

#### For `hybrid` (Numerical + Rubric):
Edit `.eval/rubric.json` with both sections:
```json
{
    "numerical_checks": [
        {"name": "Total Cost", "expected": 1500, "tolerance": 0.01, "weight": 2,
         "extraction_pattern": "Total Cost[：:]\\s*([\\d.]+)"}
    ],
    "rubric_checks": [
        {"point": "Explained the reasoning", "weight": 1}
    ]
}
```

### Step 6: Test your task

```bash
./run_eval.sh claude-code my-new-task
```

## Task Structure Reference

```
tasks/my-new-task/
├── task.yaml              # Metadata: name, category, difficulty, evaluation config
├── query.md               # Task prompt given to the agent
├── files/                 # Input files (PDFs, Excel, images, code, etc.)
│   ├── document.pdf
│   ├── data.xlsx
│   └── ...
└── .eval/
    ├── rubric.py          # Evaluation script (all types)
    ├── rubric.json        # Rubric points (llm_judge and hybrid types)
    └── ground_truth.json  # Ground truth answers (f1_match and code_exec types)
```

## Best Practices

1. **Preserve production ambiguity** — Don't over-specify requirements. If the real task is ambiguous, keep it ambiguous.
2. **Use multiple evaluation types** — Combine rubric + numerical checks when possible (avg 2.8 types per task in AlphaEval).
3. **Weight rubric points by importance** — Not all criteria are equally important.
4. **Test with multiple agents** — A good task should differentiate between strong and weak agents.
5. **Document your ground truth** — Always note how ground truth was determined and by whom.
6. **Include domain context** — If the task requires domain knowledge, provide it in the input files, not the query.

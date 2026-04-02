# AlphaEval: Evaluating Agents in Production

🌐 **Website:** [https://alphaeval.ai](https://alphaeval.ai)

A production-grounded evaluation framework for AI agents, featuring **94 tasks** sourced from **8 companies** across **6 O*NET occupational domains**.

## Overview

AlphaEval provides:
1. **A requirement-to-benchmark construction framework** — transforming authentic production requirements into executable, automated evaluations
2. **A production-grounded agent benchmark** — 94 tasks preserving real-world complexity (ambiguous specifications, multi-modal inputs, domain-specific criteria)
3. **A unified evaluation framework** — 4 evaluation paradigms (Reference Answer Verification, Formal Logic Verification, Rubric-based Evaluation, Execution-based Verification) through a standardized API with Docker-sandboxed execution
4. **An empirical analysis of the research-production gap** — the best agent configuration achieves only 64.41/100

## Task Domains (O*NET Classification)

| Domain | O*NET Code | Tasks | Description |
|--------|-----------|-------|-------------|
| Human Resources | 13-1071 | 11 | Resume screening against job descriptions |
| Finance & Investment | 13-2051 | 22 | Investment research, pitch coaching, financial data extraction |
| Procurement & Operations | 13-1020 | 23 | BOM cost optimization, procurement data analysis |
| Software Engineering | 15-1252 | 11 | Full-stack mini-program development |
| Healthcare & Life Sciences | 29-xxxx | 16 | Clinical trial eCRF management, healthcare policy analysis |
| Technology Research | 15-1221 | 11 | AI industry deep research, technical analysis |

## Quick Start

### Prerequisites

- Python 3.10+
- Docker
- API keys for the models you want to evaluate

### Setup

```bash
# Clone the repository
git clone https://github.com/GAIR-NLP/AlphaEval.git
cd AlphaEval

# Copy config template
cp config/config.example.yaml config.yaml
# Edit config.yaml with your API keys

# Install dependencies
pip install openai pyyaml
```

### Running Evaluation

```bash
# Run a single task with Claude Code
./run_eval.sh claude-code <task_id>

# Run with Codex
./run_eval.sh codex-agent <task_id>

# Run with GitHub Copilot
./run_eval.sh copilot-agent <task_id>

# Run with Cursor
./run_eval.sh cursor-agent <task_id>
```

### Supported Agent Products

| Agent | Description |
|-------|-------------|
| `claude-code` | Anthropic's CLI agent |
| `codex-agent` | OpenAI's CLI agent |
| `copilot-agent` | GitHub's coding agent |
| `cursor-agent` | Cursor's AI IDE agent |

## Task Structure

Each task follows this directory structure:

```
tasks/<task-name>/
├── task.yaml              # Task metadata and evaluation config
├── query.md               # Task prompt given to the agent
├── files/                 # Input files (PDFs, Excel, images, etc.)
└── .eval/
    ├── rubric.py          # Evaluation script
    └── ground_truth.json  # Ground truth data (if applicable)
```

## Evaluation Methods

| Paradigm | Description | Tasks |
|----------|-------------|-------|
| Reference Answer Verification | String/semantic matching against reference answers | ~11% |
| Formal Logic Verification | Mathematical proofs and code analysis | ~21% |
| Rubric-based Evaluation | LLM-as-Judge with expert-designed rubrics | ~56% |
| Execution-based Verification | Code unit testing and UI testing | ~12% |

Each task composes multiple paradigms (avg. 2.8 per task). All rubric scripts output standardized scores (0.0–1.0).

## Creating New Tasks

See `tasks/.example/` for a template. To add a new task:

1. Create a directory under `tasks/`
2. Add `task.yaml` with metadata
3. Add `query.md` with the task prompt
4. Add input files to `files/`
5. Create `.eval/rubric.py` with evaluation logic

## Key Results

| Agent Product | Model | Avg Score |
|--------------|-------|-----------|
| Claude Code | Claude Opus 4.6 | **64.41** |
| Cursor | Claude Opus 4.6 | 61.85 |
| GitHub Copilot | Claude Opus 4.6 | 61.31 |
| GitHub Copilot | GPT-5.2 | 54.91 |
| Codex | Claude Opus 4.6 | 53.45 |

Key findings:
- **Scaffold matters as much as model**: Same Opus 4.6 scores 64.41 via Claude Code but only 53.45 via Codex (11-point spread)
- **Domain variance is extreme**: Technology Research (avg 62.0) vs Human Resources (avg 30.0)
- **No single score captures production readiness**: Inter-domain rank correlations are often statistically insignificant

## Economic Value

The 94 tasks represent **2,420 professional hours** (~60 person-weeks) of labor, valued at **$154K–$231K** (USD).

## Paper

📄 **[AlphaEval: Evaluating Agents in Production (v0)](paper/AlphaEval_v0.pdf)**

> This is an early version of the paper. It will be further revised and improved. An arXiv version will be released soon.

## Citation

```bibtex
@article{alphaeval2026,
  title={AlphaEval: Evaluating Agents in Production},
  author={Anonymous},
  year={2026}
}
```

## License

MIT License - see [LICENSE](LICENSE) for details.

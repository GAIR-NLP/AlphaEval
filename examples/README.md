# Example Tasks

> **Note:** All examples in this directory are **synthetic/fictional** tasks created for demonstration purposes only. They illustrate the task structure and evaluation formats used in AlphaEval but do **not** contain real evaluation data. The actual benchmark tasks are not included in this repository to protect partner company data.

## Examples

| Example | Domain | Evaluation Type | Description |
|---------|--------|----------------|-------------|
| `poet-1` | Finance & Investment | LLM-as-Judge | Aircraft delivery data extraction from annual reports |
| `ccforqiji-1` | Finance & Investment | LLM-as-Judge | Startup pitch coaching with investor critique |
| `yuhe-1` | Procurement & Operations | Constraint Verification | BOM board card cost optimization |
| `hunter-ai-1` | Human Resources | F1 Score | Resume screening against job description |
| `miniprogram-poetry` | Software Engineering | UI Testing | Full-stack mini-program with TTS, community, and collections |

## How to Use

1. Browse the examples to understand the task format
2. Pick the evaluation template closest to your use case (see `tasks/.templates/`)
3. Copy the template and customize with your own data
4. Run with `./run_eval.sh <agent_type> <task_id>`

See [Task Creation Guide](../tasks/TASK_CREATION_GUIDE.md) for detailed instructions.

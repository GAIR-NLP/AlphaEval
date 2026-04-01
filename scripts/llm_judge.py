#!/usr/bin/env python3
"""LLM-as-a-Judge Evaluator

Evaluates agent answers against reference answers using LLM.
Uses OpenAI-compatible API (supports OpenRouter, Azure, etc.)
Returns only true/false judgment.

Usage:
    python llm_judge.py <query> <actual_answer> <reference_answer> [--config config.yaml]
"""

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)


def load_config(config_path: str = None) -> dict:
    """Load configuration from YAML file."""
    if config_path is None:
        # Default: look for config.yaml in project root
        script_dir = Path(__file__).parent.parent
        config_path = script_dir / "config.yaml"
    
    config_path = Path(config_path)
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}


def evaluate_with_llm(
    query: str,
    actual_answer: str,
    reference_answer: str,
    api_key: str,
    base_url: str = None,
    model: str = "anthropic/claude-4.5-sonnet",
) -> dict:
    """Evaluate the answer using LLM-as-a-Judge.
    
    Args:
        query: The original question/task
        actual_answer: The agent's answer
        reference_answer: The expected/reference answer
        api_key: API key
        base_url: Base URL for the API (optional)
        model: Model to use
        
    Returns:
        {"passed": true/false, "reasoning": "..."}
    """
    # Create OpenAI client
    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    
    client = OpenAI(**client_kwargs)
    
    prompt = f"""You are an evaluation judge. Determine if the agent's answer correctly answers the question.

## Question/Task
{query}

## Reference Answer (Correct)
{reference_answer}

## Agent's Answer
{actual_answer}

## Instructions
Compare the agent's answer with the reference answer. 
- Focus on correctness, not formatting
- Minor differences in wording or format are acceptable if the meaning is the same
- For numerical answers, "13", "13.0", "thirteen" are all equivalent

Respond with ONLY a JSON object (no markdown):
{{"passed": true, "reasoning": "brief explanation"}}
or
{{"passed": false, "reasoning": "brief explanation"}}
"""

    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Handle potential markdown code blocks
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])
        
        result = json.loads(response_text)
        
        # Ensure boolean
        result["passed"] = bool(result.get("passed", False))
        result.setdefault("reasoning", "")
        
        return result
        
    except json.JSONDecodeError:
        # Try to extract passed from text
        passed = "true" in response_text.lower() and "passed" in response_text.lower()
        return {
            "passed": passed,
            "reasoning": f"Parse error, raw response: {response_text[:200]}"
        }
    except Exception as e:
        return {
            "passed": False,
            "reasoning": f"Evaluation error: {str(e)}"
        }


def main():
    parser = argparse.ArgumentParser(description="LLM-as-a-Judge Evaluator")
    parser.add_argument("query", help="Original question/task")
    parser.add_argument("actual", help="Actual answer from agent")
    parser.add_argument("reference", help="Reference/expected answer")
    parser.add_argument("--config", default=None, help="Path to config.yaml")
    parser.add_argument("--model", default=None, help="Override judge model")
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    llm_config = config.get("llm", {})
    
    # Get API settings from config or environment
    api_key = llm_config.get("api_key") or os.environ.get("OPENAI_API_KEY")
    base_url = llm_config.get("base_url")
    model = args.model or llm_config.get("judge_model", "anthropic/claude-4.5-sonnet")
    
    if not api_key:
        print("Error: API key not found in config.yaml or OPENAI_API_KEY env", file=sys.stderr)
        sys.exit(1)
    
    result = evaluate_with_llm(
        query=args.query,
        actual_answer=args.actual,
        reference_answer=args.reference,
        api_key=api_key,
        base_url=base_url,
        model=model,
    )
    
    # Output result
    print(json.dumps(result, ensure_ascii=False))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("passed") else 1)


if __name__ == "__main__":
    main()

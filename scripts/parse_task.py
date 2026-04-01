#!/usr/bin/env python3
"""Parse task.yaml and output evaluation config."""

import sys
import yaml
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        print("Usage: parse_task.py <task.yaml> <field>", file=sys.stderr)
        print("Fields: eval_type, expected_answer, reference_answer, rubric_script, rubric_command, pass_pattern, pass_threshold", file=sys.stderr)
        sys.exit(1)
    
    task_yaml = sys.argv[1]
    field = sys.argv[2]
    
    try:
        with open(task_yaml, 'r') as f:
            config = yaml.safe_load(f)
        
        evaluation = config.get('evaluation', {})
        
        if field == 'eval_type':
            print(evaluation.get('type', 'exact_match'))
        elif field == 'expected_answer':
            print(evaluation.get('expected_answer', ''))
        elif field == 'reference_answer':
            print(evaluation.get('reference_answer', ''))
        elif field == 'judge_model':
            judge = evaluation.get('judge', {})
            print(judge.get('model', 'openai/gpt-4o'))
        # Code execution fields
        elif field == 'rubric_script':
            print(evaluation.get('rubric_script', ''))
        elif field == 'rubric_command':
            print(evaluation.get('rubric_command', ''))
        elif field == 'pass_pattern':
            print(evaluation.get('pass_pattern', r'score=1\.0'))
        elif field == 'pass_threshold':
            print(evaluation.get('pass_threshold', '0.0'))
        else:
            print(f"Unknown field: {field}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


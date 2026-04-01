#!/usr/bin/env python3
"""Parse Claude Code CLI stream-json output."""

import json
import sys
from pathlib import Path


def parse_stream_json(filepath: str) -> dict:
    """Parse the stream-json output from Claude Code CLI.
    
    Args:
        filepath: Path to the JSONL output file.
        
    Returns:
        Parsed result dictionary.
    """
    result = {
        "success": False,
        "agent": "claude-code",
        "steps": [],
        "final_output": None,
        "total_cost_usd": None,
        "duration_ms": 0,
        "num_turns": 0,
        "error": None,
    }
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                msg_type = data.get("type")
                
                if msg_type == "assistant":
                    # Assistant message with content
                    content = data.get("message", {}).get("content", [])
                    step_content = []
                    for block in content:
                        if block.get("type") == "text":
                            step_content.append({
                                "type": "text",
                                "text": block.get("text", "")[:500]
                            })
                        elif block.get("type") == "tool_use":
                            step_content.append({
                                "type": "tool_use",
                                "tool": block.get("name", "unknown")
                            })
                    if step_content:
                        result["steps"].append({
                            "step": len(result["steps"]),
                            "content": step_content
                        })
                        
                elif msg_type == "result":
                    # Final result
                    result["success"] = data.get("subtype") == "success"
                    result["final_output"] = data.get("result")
                    result["total_cost_usd"] = data.get("total_cost_usd")
                    result["duration_ms"] = data.get("duration_ms", 0)
                    result["num_turns"] = data.get("num_turns", 0)
                    
                    if data.get("subtype") == "error":
                        result["error"] = data.get("result")
                        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: parse_result.py <output.jsonl>", file=sys.stderr)
        sys.exit(1)
    
    filepath = sys.argv[1]
    result = parse_stream_json(filepath)
    
    # Save result
    result_file = Path("/agent_logs/agent_result.json")
    result_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"Success: {result['success']}")
    print(f"Steps: {len(result['steps'])}")
    print(f"Turns: {result['num_turns']}")
    if result['total_cost_usd']:
        print(f"Cost: ${result['total_cost_usd']:.4f}")
    if result['error']:
        print(f"Error: {result['error']}")
    print(f"Result saved to: {result_file}")
    
    # Output result as JSON for parsing
    print()
    print("=== RESULT_JSON ===")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()


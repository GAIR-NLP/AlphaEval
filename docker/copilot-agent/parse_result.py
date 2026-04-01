#!/usr/bin/env python3
"""Parse Copilot CLI output."""

import json
import os
import sys
from pathlib import Path


def parse_copilot_output(filepath: str, agent_name: str = "copilot-agent") -> dict:
    """Parse the output from Copilot CLI.
    
    Args:
        filepath: Path to the JSONL output file.
        agent_name: Name of the agent.
        
    Returns:
        Parsed result dictionary.
    """
    result = {
        "success": False,
        "agent": agent_name,
        "steps": [],
        "final_output": None,
        "total_cost_usd": None,
        "duration_ms": 0,
        "num_turns": 0,
        "error": None,
    }
    
    try:
        with open(filepath, 'r') as f:
            content = f.read().strip()
            
        # Try to parse as single JSON first
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                result["success"] = data.get("subtype") == "success" or data.get("status") == "success"
                result["final_output"] = data.get("result") or data.get("output") or data.get("text")
                result["total_cost_usd"] = data.get("total_cost_usd")
                result["duration_ms"] = data.get("duration_ms", 0)
                result["num_turns"] = data.get("num_turns", 1)
                
                if data.get("error"):
                    result["error"] = data.get("error")
                    result["success"] = False
                    
                return result
        except json.JSONDecodeError:
            pass
            
        # Parse as JSONL
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                # Plain text output
                if line and not line.startswith('#'):
                    result["steps"].append({
                        "step": len(result["steps"]),
                        "content": [{"type": "text", "text": line[:500]}]
                    })
                continue
            
            msg_type = data.get("type")
            
            if msg_type == "assistant" or msg_type == "message":
                content_data = data.get("message", {}).get("content", [])
                if isinstance(content_data, str):
                    content_data = [{"type": "text", "text": content_data}]
                    
                step_content = []
                for block in content_data:
                    if isinstance(block, str):
                        step_content.append({"type": "text", "text": block[:500]})
                    elif isinstance(block, dict):
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
                    
            elif msg_type == "result" or msg_type == "complete":
                result["success"] = data.get("subtype") == "success" or data.get("status") == "success"
                result["final_output"] = data.get("result") or data.get("output")
                result["total_cost_usd"] = data.get("total_cost_usd")
                result["duration_ms"] = data.get("duration_ms", 0)
                result["num_turns"] = data.get("num_turns", 0)
                
                if data.get("subtype") == "error" or data.get("error"):
                    result["error"] = data.get("result") or data.get("error")
                    result["success"] = False
                    
    except Exception as e:
        result["error"] = str(e)
    
    # If no explicit result, consider success if we have steps
    if not result["success"] and result["steps"]:
        result["success"] = True
    
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: parse_result.py <output.jsonl> [agent_name]", file=sys.stderr)
        sys.exit(1)
    
    filepath = sys.argv[1]
    agent_name = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("AGENT_NAME", "copilot-agent")
    result = parse_copilot_output(filepath, agent_name)
    
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

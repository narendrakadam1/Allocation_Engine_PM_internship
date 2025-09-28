import json, ast
from typing import Any, Dict

def safe_parse(obj: Any) -> Dict:
    """
    Robust parser for orchestrator/matcher outputs.
    Always returns a dict so UI doesn't crash.
    """
    if obj is None:
        return {}

    if isinstance(obj, dict):
        return obj

    if isinstance(obj, str):
        text = obj.strip()

        # Try JSON
        try:
            return json.loads(text)
        except Exception:
            pass

        # Try Python dict-like string
        try:
            return ast.literal_eval(text)
        except Exception:
            pass

        # Fallback: wrap raw string
        return {"raw_output": text}

    # Fallback for other types
    return {"raw_output": str(obj)}

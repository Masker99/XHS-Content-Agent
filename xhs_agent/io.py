from __future__ import annotations

import json
from typing import Any


def normalize_openclaw_instruction(payload: str | dict[str, Any]) -> tuple[str, str]:
    """Accept a plain instruction or an OpenClaw-style JSON payload."""

    if isinstance(payload, dict):
        return json.dumps(payload, ensure_ascii=False, indent=2), "openclaw"

    text = payload.strip()
    if not text:
        raise ValueError("Instruction cannot be empty.")

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return text, "text"

    if isinstance(parsed, dict):
        return json.dumps(parsed, ensure_ascii=False, indent=2), "openclaw"
    
    return text, "text"

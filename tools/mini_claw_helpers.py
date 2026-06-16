from __future__ import annotations

import json
from typing import Any

from utils.tools import _safe_get

def estimate_tokens(text: Any) -> int:
    """Rough token count estimation: 1 token per 4 chars, minimum 1."""
    s = str(text or "")
    return max(1, (len(s) // 4) + 1)

def message_to_text(msg: Any) -> str:
    """Extract text content from a message object (could be Dify message or dict)."""
    content = getattr(msg, "content", None)
    if content is None:
        content = _safe_get(msg, "content")
    if isinstance(content, list):
        acc: list[str] = []
        for item in content:
            if isinstance(item, dict):
                t = item.get("text") or item.get("content") or item.get("data") or ""
                if t:
                    acc.append(str(t))
            elif item:
                acc.append(str(item))
        return "\n".join(acc).strip()
    if isinstance(content, dict):
        return json.dumps(content, ensure_ascii=False)
    return str(content or "").strip()

def estimate_prompt_tokens(msgs: list[Any]) -> int:
    """Sum estimated tokens across a list of messages."""
    total = 0
    for m in msgs:
        total += estimate_tokens(message_to_text(m))
    return total

def _user_explicitly_requested_skill(text: Any, *, skill_id: str, display_name: str) -> bool:
    """Check if user's text explicitly mentions a skill by ID or display name."""
    s = str(text or "")
    if not s:
        return False
    s_lower = s.lower()
    sid = str(skill_id or "").strip().lower()
    if sid and sid in s_lower:
        return True
    dn = str(display_name or "").strip().lower()
    if dn and dn in s_lower:
        return True
    return False

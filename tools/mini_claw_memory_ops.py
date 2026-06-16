from __future__ import annotations

import time
from typing import Any


def _norm_kv(d: Any) -> dict[str, str]:
    """Normalize a key-value dict: strip, truncate keys to 24 chars, values to 200."""
    if not isinstance(d, dict):
        return {}
    out: dict[str, str] = {}
    for k, v in d.items():
        kk = str(k or "").strip()
        vv = str(v or "").strip()
        if not kk or not vv:
            continue
        if len(kk) > 24:
            kk = kk[:24]
        if len(vv) > 200:
            vv = vv[:200]
        out[kk] = vv
    return out


def _norm_list(xs: Any) -> list[str]:
    """Normalize a list of strings: strip, deduplicate, truncate each to 240."""
    if not isinstance(xs, list):
        return []
    out: list[str] = []
    for x in xs:
        s = str(x or "").strip()
        if not s:
            continue
        if len(s) > 240:
            s = s[:240]
        if s not in out:
            out.append(s)
    return out


def _render_section(title: str, kv: dict[str, str]) -> list[str]:
    """Render a markdown section with sorted key-value pairs."""
    if not kv:
        return [f"### {title}", "- (empty)"]
    out_lines = [f"### {title}"]
    for k in sorted(kv.keys()):
        out_lines.append(f"- **{k}:** {kv[k]}")
    return out_lines


def _render_list_section(title: str, items: list[str]) -> list[str]:
    """Render a markdown section with bullet list items."""
    if not items:
        return [f"### {title}", "- (empty)"]
    out_lines = [f"### {title}"]
    for it in items:
        out_lines.append(f"- {it}")
    return out_lines


def _memory_merge_managed_block(existing_memory_md: Any, updates: dict[str, Any]) -> str:
    """Merge extracted memory updates into the 'Managed Memory (auto)' block of MEMORY.md."""
    existing = str(existing_memory_md or "").strip()
    if not existing:
        existing = "# MEMORY.md - Long-term Memory\n\n"

    user_prefs = _norm_kv(updates.get("user_preferences"))
    project_facts = _norm_kv(updates.get("project_facts"))
    decisions = _norm_list(updates.get("decisions"))

    marker = "## Managed Memory (auto)"
    lines = existing.splitlines()
    start = -1
    for i, line in enumerate(lines):
        if line.strip() == marker:
            start = i
            break
    if start != -1:
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("## ") and lines[j].strip() != marker:
                end = j
                break
        preserved = "\n".join(lines[:start]).rstrip() + "\n\n" + "\n".join(lines[end:]).lstrip()
        existing = preserved.strip() + "\n"

    managed: list[str] = [marker]
    managed.append(f"- updated_at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    managed.append("")
    managed.extend(_render_section("User Preferences", user_prefs))
    managed.append("")
    managed.extend(_render_section("Project Facts", project_facts))
    managed.append("")
    managed.extend(_render_list_section("Decisions", decisions))
    managed.append("")

    return existing.rstrip() + "\n\n" + "\n".join(managed)

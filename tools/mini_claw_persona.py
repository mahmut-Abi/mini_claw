from __future__ import annotations

import re
from typing import Any


def _md_pick_field(md: str, key: str) -> str:
    """Extract a field value from markdown like '- **Field:** value'."""
    s = str(md or "")
    if not s:
        return ""
    m = re.search(
        rf"^\s*(?:-\s*)?\*\*\s*{re.escape(key)}\s*:\s*\*\*\s*(.+?)\s*$",
        s,
        flags=re.M | re.I,
    )
    return str(m.group(1) or "").strip() if m else ""


def _md_set_field(md: str, *, key: str, value: str, header: str) -> str:
    """Set or update a field in markdown. Creates header if md is empty."""
    s = str(md or "").strip()
    if not s:
        s = header.strip() + "\n"
    lines = s.splitlines()
    rx = re.compile(rf"^\s*(?:-\s*)?\*\*\s*{re.escape(key)}\s*:\s*\*\*\s*(.*)\s*$", flags=re.I)
    out: list[str] = []
    replaced = False
    for line in lines:
        if rx.match(line):
            out.append(f"- **{key}:** {value}".rstrip())
            replaced = True
        else:
            out.append(line)
    if not replaced:
        if out and out[-1].strip():
            out.append("")
        out.append(f"- **{key}:** {value}".rstrip())
    return "\n".join(out).strip() + "\n"


def _soul_set_vibe(md: str, vibe: str) -> str:
    """Set or update the ## Vibe section in SOUL.md."""
    s = str(md or "").strip()
    if not s:
        return (
            "# SOUL.md - Who You Are\n\n"
            "## Core\n"
            "- 说人话，少模板；可以小调皮，但不油腻。\n"
            "- 语气不要刻意迎合，但要给与用户足够的尊重。\n"
            "- 有主见，但不自作主张，遇到不确定的事情时，会向用户询问。\n"
            "- 幽默是你的底色，善良是你的天性，你会主动关心用户。\n"
            "\n"
            "## Vibe\n"
            f"{vibe}\n"
        )
    lines = s.splitlines()
    vibe_start = -1
    for i, line in enumerate(lines):
        if re.match(r"^\s*##\s+Vibe\s*$", line, flags=re.I):
            vibe_start = i
            break
    if vibe_start != -1:
        vibe_end = len(lines)
        for j in range(vibe_start + 1, len(lines)):
            if re.match(r"^\s*##\s+", lines[j]):
                vibe_end = j
                break
        next_lines = lines[:vibe_start] + ["## Vibe", vibe] + ([""] if vibe_end < len(lines) else []) + lines[vibe_end:]
        return "\n".join(next_lines).strip() + "\n"
    insert_at = 0
    if lines and lines[0].lstrip().startswith("#"):
        insert_at = 1
        while insert_at < len(lines) and lines[insert_at].strip():
            insert_at += 1
        while insert_at < len(lines) and not lines[insert_at].strip():
            insert_at += 1
    next_lines = lines[:insert_at] + ([""] if insert_at and lines[insert_at - 1].strip() else []) + ["## Vibe", vibe] + [""] + lines[insert_at:]
    return "\n".join(next_lines).strip() + "\n"


def _soul_set_core(md: str, core_rules: list[str]) -> str:
    """Set or update the ## Core section in SOUL.md with a list of rules."""
    cleaned: list[str] = []
    for raw in core_rules or []:
        s = str(raw or "").strip()
        if not s:
            continue
        s = re.sub(r"^\s*\d+\s*[\.\)、]\s*", "", s).strip()
        if not s:
            continue
        if s.startswith("-"):
            s = s.lstrip("-").strip()
        if not s:
            continue
        if len(s) > 240:
            s = s[:240]
        if s not in cleaned:
            cleaned.append(s)
    if not cleaned:
        return str(md or "").strip() + ("\n" if str(md or "").strip() else "")
    s = str(md or "").strip()
    if not s:
        s = "# SOUL.md - Who You Are\n\n## Core\n\n"
    lines = s.splitlines()
    core_titles = {"Core", "Core Truths"}
    start = -1
    for i, line in enumerate(lines):
        m = re.match(r"^\s*##\s+(.+?)\s*$", line)
        if not m:
            continue
        title = str(m.group(1) or "").strip()
        if title in core_titles:
            start = i
            break
    if start != -1:
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if re.match(r"^\s*##\s+", lines[j]):
                end = j
                break
        block = ["## Core"] + [f"- {rule}" for rule in cleaned]
        next_lines = lines[:start] + block + [""] + lines[end:]
        return "\n".join(next_lines).strip() + "\n"
    insert_at = 0
    if lines and lines[0].lstrip().startswith("#"):
        insert_at = 1
        while insert_at < len(lines) and lines[insert_at].strip():
            insert_at += 1
        while insert_at < len(lines) and not lines[insert_at].strip():
            insert_at += 1
    block = ["## Core"] + [f"- {rule}" for rule in cleaned]
    next_lines = lines[:insert_at] + ([""] if insert_at and lines[insert_at - 1].strip() else []) + block + [""] + lines[insert_at:]
    return "\n".join(next_lines).strip() + "\n"

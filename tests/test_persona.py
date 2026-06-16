from __future__ import annotations

import pytest

from tools.mini_claw_persona import (
    _md_pick_field,
    _md_set_field,
    _soul_set_core,
    _soul_set_vibe,
)


class TestMdPickField:
    def test_extracts_existing_field(self):
        md = "- **Name:** Alice\n- **Age:** 30\n"
        assert _md_pick_field(md, "Name") == "Alice"
        assert _md_pick_field(md, "Age") == "30"

    def test_returns_empty_for_missing_field(self):
        md = "- **Name:** Alice\n"
        assert _md_pick_field(md, "Age") == ""

    def test_returns_empty_for_empty_md(self):
        assert _md_pick_field("", "Name") == ""
        assert _md_pick_field("   ", "Name") == ""


class TestMdSetField:
    def test_updates_existing_field(self):
        md = "- **Name:** Alice\n- **Age:** 30\n"
        result = _md_set_field(md, key="Name", value="Bob", header="# HEADER")
        assert "**Name:** Bob" in result
        assert "**Age:** 30" in result

    def test_adds_new_field(self):
        md = "- **Name:** Alice\n"
        result = _md_set_field(md, key="Age", value="30", header="# HEADER")
        assert "**Name:** Alice" in result
        assert "**Age:** 30" in result

    def test_creates_from_empty_md_with_header(self):
        result = _md_set_field("", key="Name", value="Alice", header="# HEADER")
        assert result.startswith("# HEADER")
        assert "**Name:** Alice" in result


class TestSoulSetVibe:
    def test_updates_existing_vibe_section(self):
        md = "# SOUL.md\n\n## Core\n- rule1\n\n## Vibe\nold vibe\n\n## Other\nstuff\n"
        result = _soul_set_vibe(md, "new vibe")
        assert "new vibe" in result
        assert "old vibe" not in result
        assert "## Core" in result
        assert "## Other" in result

    def test_adds_vibe_to_md_without_one(self):
        md = "# SOUL.md\n\n## Core\n- rule1\n"
        result = _soul_set_vibe(md, "chill")
        assert "## Vibe" in result
        assert "chill" in result
        assert "## Core" in result

    def test_creates_from_empty(self):
        result = _soul_set_vibe("", "playful")
        assert "SOUL.md" in result
        assert "## Vibe" in result
        assert "playful" in result
        assert "## Core" in result


class TestSoulSetCore:
    def test_replaces_existing_core(self):
        md = "# SOUL.md\n\n## Core\n- old1\n- old2\n\n## Vibe\nstuff\n"
        result = _soul_set_core(md, ["new1", "new2"])
        assert "- new1" in result
        assert "- new2" in result
        assert "- old1" not in result
        assert "## Vibe" in result

    def test_adds_core_section(self):
        md = "# SOUL.md\n\n## Vibe\nstuff\n"
        result = _soul_set_core(md, ["be kind"])
        assert "## Core" in result
        assert "- be kind" in result
        assert "## Vibe" in result

    def test_handles_empty_rules_list(self):
        md = "# SOUL.md\n\n## Core\n- old\n"
        result = _soul_set_core(md, [])
        assert result == md

    def test_handles_numbered_list_input(self):
        md = "# SOUL.md\n\n## Core\n- old\n"
        result = _soul_set_core(md, ["1. be nice", "2. work hard"])
        assert "- be nice" in result
        assert "- work hard" in result
        assert "1." not in result
        assert "2." not in result

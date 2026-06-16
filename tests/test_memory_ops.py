from __future__ import annotations

import pytest
from tools.mini_claw_memory_ops import (
    _norm_kv,
    _norm_list,
    _render_section,
    _render_list_section,
    _memory_merge_managed_block,
)


class TestNormKv:
    def test_normal_key_values(self) -> None:
        result = _norm_kv({"name": "Alice", "role": "admin"})
        assert result == {"name": "Alice", "role": "admin"}

    def test_strips_whitespace(self) -> None:
        result = _norm_kv({"  key  ": "  val  "})
        assert result == {"key": "val"}

    def test_empty_keys_and_values_skipped(self) -> None:
        result = _norm_kv({"": "val", "key": "", "  ": "x", "k": "  "})
        assert result == {}

    def test_empty_dict(self) -> None:
        result = _norm_kv({})
        assert result == {}

    def test_non_dict_input(self) -> None:
        assert _norm_kv(None) == {}
        assert _norm_kv(42) == {}
        assert _norm_kv("string") == {}
        assert _norm_kv([]) == {}

    def test_truncation_long_key(self) -> None:
        long_key = "a" * 30
        result = _norm_kv({long_key: "value"})
        assert result == {"a" * 24: "value"}

    def test_truncation_long_value(self) -> None:
        long_val = "b" * 250
        result = _norm_kv({"key": long_val})
        assert result == {"key": "b" * 200}

    def test_none_keys_and_values(self) -> None:
        result = _norm_kv({None: None})
        assert result == {}

    def test_non_string_keys_and_values(self) -> None:
        result = _norm_kv({42: 99})
        assert result == {"42": "99"}


class TestNormList:
    def test_normal_list(self) -> None:
        result = _norm_list(["alpha", "beta", "gamma"])
        assert result == ["alpha", "beta", "gamma"]

    def test_strips_whitespace(self) -> None:
        result = _norm_list(["  hello  ", " world "])
        assert result == ["hello", "world"]

    def test_empty_list(self) -> None:
        assert _norm_list([]) == []

    def test_non_list_input(self) -> None:
        assert _norm_list(None) == []
        assert _norm_list(42) == []
        assert _norm_list("string") == []
        assert _norm_list({}) == []

    def test_deduplication(self) -> None:
        result = _norm_list(["a", "b", "a", "c", "b"])
        assert result == ["a", "b", "c"]

    def test_truncation(self) -> None:
        long_str = "x" * 300
        result = _norm_list([long_str])
        assert result == ["x" * 240]

    def test_skip_empty_strings(self) -> None:
        result = _norm_list(["", "  ", "valid", ""])
        assert result == ["valid"]

    def test_none_and_non_string_items(self) -> None:
        result = _norm_list([None, 42, True, 3.14])
        assert result == ["42", "True", "3.14"]


class TestRenderSection:
    def test_with_data(self) -> None:
        result = _render_section("Facts", {"a": "1", "b": "2"})
        assert result[0] == "### Facts"
        assert "- **a:** 1" in result
        assert "- **b:** 2" in result

    def test_sorted_keys(self) -> None:
        result = _render_section("Prefs", {"z": "last", "a": "first"})
        # a should come before z
        a_idx = next(i for i, s in enumerate(result) if "- **a:**" in s)
        z_idx = next(i for i, s in enumerate(result) if "- **z:**" in s)
        assert a_idx < z_idx

    def test_empty_dict(self) -> None:
        result = _render_section("Empty", {})
        assert result == ["### Empty", "- (empty)"]


class TestRenderListSection:
    def test_with_items(self) -> None:
        result = _render_list_section("Items", ["one", "two"])
        assert result == ["### Items", "- one", "- two"]

    def test_empty_list(self) -> None:
        result = _render_list_section("Empty", [])
        assert result == ["### Empty", "- (empty)"]


class TestMemoryMergeManagedBlock:
    def test_empty_existing_with_updates(self) -> None:
        result = _memory_merge_managed_block("", {
            "user_preferences": {"theme": "dark"},
            "project_facts": {"name": "mini_claw"},
            "decisions": ["use python"],
        })
        assert "## Managed Memory (auto)" in result
        assert "updated_at:" in result
        assert "### User Preferences" in result
        assert "**theme:** dark" in result
        assert "### Project Facts" in result
        assert "**name:** mini_claw" in result
        assert "### Decisions" in result
        assert "- use python" in result

    def test_none_existing_with_updates(self) -> None:
        result = _memory_merge_managed_block(None, {
            "user_preferences": {"lang": "en"},
        })
        assert "# MEMORY.md - Long-term Memory" in result
        assert "## Managed Memory (auto)" in result

    def test_old_managed_block_replaced(self) -> None:
        existing = (
            "# MEMORY.md\n\n"
            "some content\n\n"
            "## Managed Memory (auto)\n"
            "- old data\n\n"
            "## Other Section\n"
            "keep this\n"
        )
        result = _memory_merge_managed_block(existing, {
            "user_preferences": {"new_key": "new_val"},
        })
        assert "## Other Section" in result
        assert "keep this" in result
        assert "old data" not in result
        assert "**new_key:** new_val" in result

    def test_managed_block_at_end(self) -> None:
        existing = (
            "# MEMORY.md\n\n"
            "## Another Section\n"
            "data\n\n"
            "## Managed Memory (auto)\n"
            "- old stuff\n"
        )
        result = _memory_merge_managed_block(existing, {})
        assert "## Another Section" in result
        assert "old stuff" not in result
        assert "### User Preferences" in result
        assert "### Decisions" in result

    def test_no_updates_produces_empty_sections(self) -> None:
        result = _memory_merge_managed_block("# MEMORY.md\n", {})
        assert "### User Preferences" in result
        assert "- (empty)" in result
        assert "### Project Facts" in result
        assert "### Decisions" in result

    def test_non_string_existing_handled(self) -> None:
        result = _memory_merge_managed_block(42, {})
        assert "## Managed Memory (auto)" in result

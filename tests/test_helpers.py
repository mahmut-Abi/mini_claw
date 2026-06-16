from __future__ import annotations

from tools.mini_claw_helpers import (
    estimate_tokens,
    estimate_prompt_tokens,
    message_to_text,
    _user_explicitly_requested_skill,
)


class TestEstimateTokens:
    def test_empty_string(self):
        assert estimate_tokens("") == 1

    def test_short_string(self):
        assert estimate_tokens("abcd") == 2

    def test_long_string(self):
        assert estimate_tokens("a" * 40) == 11

    def test_none(self):
        assert estimate_tokens(None) == 1


class TestMessageToText:
    def test_simple_content(self):
        msg = type("Msg", (), {"content": "hello"})()
        assert message_to_text(msg) == "hello"

    def test_list_content(self):
        msg = type("Msg", (), {"content": [{"text": "hello"}, {"text": "world"}]})()
        assert message_to_text(msg) == "hello\nworld"

    def test_dict_content(self):
        msg = type("Msg", (), {"content": {"key": "value"}})()
        result = message_to_text(msg)
        assert "key" in result
        assert "value" in result

    def test_missing_content(self):
        msg = type("Msg", (), {})()
        assert message_to_text(msg) == ""

    def test_dict_item_with_content_key(self):
        msg = type("Msg", (), {"content": [{"content": "alt"}, {"data": "binary"}]})()
        assert message_to_text(msg) == "alt\nbinary"


class TestEstimatePromptTokens:
    def test_simple_messages(self):
        msgs = [
            type("Msg", (), {"content": "abcd"})(),
            type("Msg", (), {"content": "12345678"})(),
        ]
        assert estimate_prompt_tokens(msgs) == 5

    def test_empty_list(self):
        assert estimate_prompt_tokens([]) == 0


class TestUserExplicitlyRequestedSkill:
    def test_exact_match_by_id(self):
        assert _user_explicitly_requested_skill(
            "use find-skills", skill_id="find-skills", display_name="Find Skills"
        ) is True

    def test_case_insensitive(self):
        assert _user_explicitly_requested_skill(
            "USE FIND-SKILLS", skill_id="find-skills", display_name="Find Skills"
        ) is True

    def test_match_by_display_name(self):
        assert _user_explicitly_requested_skill(
            "I need Find Skills help", skill_id="fs", display_name="Find Skills"
        ) is True

    def test_no_match(self):
        assert _user_explicitly_requested_skill(
            "do something else", skill_id="find-skills", display_name="Find Skills"
        ) is False

    def test_empty_text(self):
        assert _user_explicitly_requested_skill(
            "", skill_id="find-skills", display_name="Find Skills"
        ) is False

    def test_none_text(self):
        assert _user_explicitly_requested_skill(
            None, skill_id="find-skills", display_name="Find Skills"
        ) is False

    def test_empty_skill_id_and_display_name(self):
        assert _user_explicitly_requested_skill(
            "some text", skill_id="", display_name=""
        ) is False

from __future__ import annotations

import base64
import os
import tempfile

from tools.mini_claw_vision import _ensure_base64_data


def test_ensure_base64_data_has_existing_b64() -> None:
    entry = {"base64_data": "YWJjMTIz", "abs_path": "/nonexistent"}
    result = _ensure_base64_data(entry)
    assert result == "YWJjMTIz"


def test_ensure_base64_data_from_real_file() -> None:
    content = b"hello world from mini_claw"
    expected_b64 = base64.b64encode(content).decode("ascii")

    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(content)
        tmp_path = tf.name

    try:
        entry: dict[str, str] = {"abs_path": tmp_path}
        result = _ensure_base64_data(entry)
        assert result == expected_b64
        assert entry["base64_data"] == expected_b64
    finally:
        os.unlink(tmp_path)


def test_ensure_base64_data_side_effect_sets_key() -> None:
    content = b"side effect test"
    expected_b64 = base64.b64encode(content).decode("ascii")

    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(content)
        tmp_path = tf.name

    try:
        entry: dict[str, str] = {"abs_path": tmp_path}
        result = _ensure_base64_data(entry)
        assert result == expected_b64
        assert "base64_data" in entry
        assert entry["base64_data"] == expected_b64
    finally:
        os.unlink(tmp_path)


def test_ensure_base64_data_no_data_no_path() -> None:
    entry: dict[str, str] = {}
    result = _ensure_base64_data(entry)
    assert result == ""


def test_ensure_base64_data_invalid_path() -> None:
    entry = {"abs_path": "/definitely/does/not/exist.txt"}
    result = _ensure_base64_data(entry)
    assert result == ""


def test_ensure_base64_data_empty_strings() -> None:
    entry = {"base64_data": "", "abs_path": ""}
    result = _ensure_base64_data(entry)
    assert result == ""


def test_ensure_base64_data_whitespace_base64() -> None:
    entry = {"base64_data": "   YWJjMTIz   "}
    result = _ensure_base64_data(entry)
    assert result == "YWJjMTIz"

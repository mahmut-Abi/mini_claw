from __future__ import annotations

import logging
import os
import re
from collections.abc import Callable, Generator
from decimal import Decimal
from typing import Any

from dify_plugin.entities.tool import ToolInvokeMessage
from utils.mini_claw_storage import _storage_get_text
from utils.tools import _guess_mime_type, _list_dir, _safe_get, _safe_join

logger = logging.getLogger("mini_claw")


# ── debug ──────────────────────────────────────────────────────────────


def _dbg(msg: str) -> None:
    logger.debug("[skill] %s", msg)


def _model_brief(model_config: Any) -> str:
    if isinstance(model_config, dict):
        provider = model_config.get("provider")
        model = model_config.get("model")
        mode = model_config.get("mode")
        return f"provider={provider!s} model={model!s} mode={mode!s}"
    provider = _safe_get(model_config, "provider")
    model = _safe_get(model_config, "model")
    mode = _safe_get(model_config, "mode")
    return f"provider={provider!s} model={model!s} mode={mode!s}"


# ── agent header ───────────────────────────────────────────────────────


def build_agent_tag_header(
    *,
    storage: Any,
    identity_key: str,
    identity_md: str | None,
    default_name: str = "Mini_Claw",
    default_emoji: str = "🤖",
) -> str:
    def pick_field(md: str, keys: list[str]) -> str:
        s = str(md or "")
        if not s:
            return ""
        for k in keys:
            rx = re.compile(
                rf"^\s*(?:-\s*)?\*\*\s*{re.escape(k)}\s*:\s*\*\*\s*(.+?)\s*$",
                flags=re.M | re.I,
            )
            m = rx.search(s)
            if m:
                return str(m.group(1) or "").strip()
        return ""

    identity_text = ""
    try:
        identity_text = _storage_get_text(storage, identity_key).strip()
    except Exception:
        identity_text = ""
    if not identity_text:
        try:
            identity_text = str(identity_md or "").strip()
        except Exception:
            identity_text = ""

    name = pick_field(identity_text, ["Name", "名字", "称呼"])
    emoji = pick_field(identity_text, ["Emoji", "表情", "签名", "签名Emoji"])
    name = re.sub(r"\s+", " ", name).strip() if name else ""
    emoji = re.sub(r"\s+", " ", emoji).strip() if emoji else ""
    if not name:
        name = default_name
    if not emoji:
        emoji = default_emoji
    return f"【{emoji}{name}】" if emoji else f"【{name}】"


# ── stream ─────────────────────────────────────────────────────────────


def stream_text_to_user(
    *,
    create_text_message: Callable[[str], ToolInvokeMessage],
    text: str,
    chunk_size: int = 8,
) -> Generator[ToolInvokeMessage, None, None]:
    s = (text or "").strip()
    if not s:
        return
    step = max(1, int(chunk_size))
    for i in range(0, len(s), step):
        yield create_text_message(s[i : i + step])


# ── usage ──────────────────────────────────────────────────────────────


class LLMUsageAccumulator:
    def __init__(self) -> None:
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.prompt_price = Decimal("0")
        self.completion_price = Decimal("0")
        self.total_price = Decimal("0")
        self.currency = ""
        self.latency = 0.0

    def _to_int(self, v: Any) -> int:
        try:
            return int(v or 0)
        except Exception:
            return 0

    def _to_float(self, v: Any) -> float:
        try:
            return float(v or 0.0)
        except Exception:
            return 0.0

    def _to_decimal(self, v: Any) -> Decimal:
        if v is None:
            return Decimal("0")
        if isinstance(v, Decimal):
            return v
        try:
            return Decimal(str(v))
        except Exception:
            return Decimal("0")

    def record_usage_obj(self, usage: Any) -> None:
        if not usage:
            return
        self.prompt_tokens += self._to_int(_safe_get(usage, "prompt_tokens"))
        self.completion_tokens += self._to_int(_safe_get(usage, "completion_tokens"))
        self.total_tokens += self._to_int(_safe_get(usage, "total_tokens"))
        self.prompt_price += self._to_decimal(_safe_get(usage, "prompt_price"))
        self.completion_price += self._to_decimal(_safe_get(usage, "completion_price"))
        self.total_price += self._to_decimal(_safe_get(usage, "total_price"))
        cur = str(_safe_get(usage, "currency") or "").strip()
        if cur:
            if not self.currency:
                self.currency = cur
            elif self.currency != cur:
                self.currency = "MIXED"
        self.latency += self._to_float(_safe_get(usage, "latency"))

    def record_response(self, resp: Any) -> None:
        if not resp:
            return
        self.record_usage_obj(_safe_get(resp, "usage"))

    def record_chunk(self, chunk: Any) -> None:
        if not chunk:
            return
        delta = _safe_get(chunk, "delta")
        self.record_usage_obj(_safe_get(delta, "usage") if delta is not None else None)

    def payload(self) -> dict[str, Any]:
        return {
            "prompt_tokens": int(self.prompt_tokens),
            "completion_tokens": int(self.completion_tokens),
            "total_tokens": int(self.total_tokens),
            "prompt_price": str(self.prompt_price),
            "completion_price": str(self.completion_price),
            "total_price": str(self.total_price),
            "currency": str(self.currency or ""),
            "latency": float(self.latency),
        }

    def format_text(self, payload: dict[str, Any] | None = None) -> str:
        p = payload or self.payload()
        prompt_tokens = int(p.get("prompt_tokens") or 0)
        completion_tokens = int(p.get("completion_tokens") or 0)
        total_tokens = int(p.get("total_tokens") or 0)
        prompt_price = str(p.get("prompt_price") or "0")
        completion_price = str(p.get("completion_price") or "0")
        total_price = str(p.get("total_price") or "0")
        currency = str(p.get("currency") or "")
        return (
            f"\n📊 Token/费用 消耗统计：\n"
            f"  ✒️输入：{prompt_tokens} tokens\n"
            f"  ✒️输出：{completion_tokens} tokens\n"
            f"  ✒️总计：{total_tokens} tokens\n"
            f"  💰输入费用：{prompt_price} 元\n"
            f"  💰输出费用：{completion_price} 元\n"
            f"  💰总费用：{total_price} 元\n"
            f"  💵币种：{currency} \n"
        )


# ── uploads ────────────────────────────────────────────────────────────


def _build_uploads_context(session_dir: str, *, max_files: int = 50) -> str:
    uploads_dir = _safe_join(session_dir, "uploads")
    if not os.path.isdir(uploads_dir):
        return ""
    entries = _list_dir(uploads_dir, max_depth=2)
    files: list[dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        if e.get("type") != "file":
            continue
        rel = str(e.get("relative_path") or "").replace("\\", "/").lstrip("/")
        path = str(e.get("path") or "")
        if not rel or not path:
            continue
        filename = os.path.basename(rel)
        mime = ""
        try:
            mime = _guess_mime_type(filename)
        except Exception:
            mime = ""
        size = 0
        try:
            size = os.path.getsize(path)
        except Exception:
            size = 0
        files.append({"relative_path": f"uploads/{rel}", "bytes": size, "mime_type": mime, "filename": filename})
    if not files:
        return ""
    files = sorted(files, key=lambda x: str(x.get("relative_path") or ""))
    files = files[: max(1, int(max_files or 50))]
    lines = [
        "\n\n[上传文件]",
        f"用户本次通过 files 参数上传的文件会保存到：{uploads_dir}",
        "请使用 read_temp_file(relative_path) 读取文件；需要把文件传给命令时，用 read_temp_file 返回的绝对路径（result.path）。",
        "",
        "[上传文件清单]",
        "以下路径均相对于本次会话的 session_dir：",
    ]
    for f in files:
        rel = str(f.get("relative_path") or "")
        abs_path = _safe_join(session_dir, rel) if rel else ""
        lines.append(
            f"- {rel} | abs={abs_path} | mime={f.get('mime_type') or ''} | bytes={f.get('bytes') or 0} | filename={f.get('filename') or ''}"
        )
    return "\n".join(lines) + "\n"

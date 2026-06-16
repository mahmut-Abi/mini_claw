from __future__ import annotations

import base64
import os
from typing import Any


def _ensure_base64_data(entry: dict[str, Any]) -> str:
    b64 = str(entry.get("base64_data") or "").strip()
    if b64:
        return b64
    path = str(entry.get("abs_path") or "").strip()
    if not path or not os.path.isfile(path):
        return ""
    try:
        with open(path, "rb") as f:
            raw = f.read()
        b64 = base64.b64encode(raw).decode("ascii")
    except Exception:
        return ""
    entry["base64_data"] = b64
    return b64

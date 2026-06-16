from __future__ import annotations

import logging
from typing import Any

from utils.tools import _safe_get

logger = logging.getLogger("mini_claw")


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

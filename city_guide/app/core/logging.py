from __future__ import annotations

import json
import logging
import os
from typing import Any, MutableMapping


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        payload: MutableMapping[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    if os.getenv("CITY_GUIDE_LOG_FORMAT", "json").lower() in {"text", "console"}:
        formatter = logging.Formatter("%(levelname)s %(name)s - %(message)s")
    else:
        formatter = JsonFormatter()
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]


configure_logging()

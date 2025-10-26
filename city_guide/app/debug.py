"""Утилита для запуска приложения в режиме отладки PyCharm.

Скрипт запускает Uvicorn без авто-перезагрузки, чтобы не плодить процессы,
которые мешают ставить брейкпоинты во встроенном дебаггере IDE. Все
настройки берутся из ``.env`` (см. :mod:`city_guide.app.core.config`).
"""

from __future__ import annotations

import uvicorn

from .core.config import settings


def main() -> None:
    """Запустить сервис с параметрами из конфигурации."""

    uvicorn.run(
        "city_guide.app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()

"""Утилита для запуска приложения в режиме отладки PyCharm.

Скрипт запускает Uvicorn без авто-перезагрузки, чтобы не плодить процессы,
которые мешают ставить брейкпоинты во встроенном дебаггере IDE. Все
настройки берутся из ``.env`` (см. :mod:`city_guide.app.core.config`).
"""

from __future__ import annotations

import sys
from pathlib import Path

import uvicorn


def _ensure_project_root_on_path() -> None:
    """Добавить корень репозитория в ``sys.path`` при запуске как скрипта.

    PyCharm по умолчанию использует конфигурацию типа ``Python`` и запускает
    целевой файл напрямую (``python path/to/debug.py``). В таком режиме Python
    помещает в ``sys.path`` только директорию файла (``city_guide/app``), из-за
    чего относительные импорты модуля не работают. Чтобы модуль оставался
    работоспособным и в конфигурациях ``Module name`` и ``Script path``,
    принудительно добавляем корень проекта в путь поиска модулей.
    """

    project_root = Path(__file__).resolve().parents[2]
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)


_ensure_project_root_on_path()

from city_guide.app.core.config import settings


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

# City Guide API

City Guide API — сервис на FastAPI, формирующий персональные прогулочные маршруты по городу.

## Содержание

- [Возможности](#возможности)
- [Требования](#требования)
- [Быстрая настройка окружения](#быстрая-настройка-окружения)
- [Отладка в PyCharm](#отладка-в-pycharm)
- [Запуск и команды Make](#запуск-и-команды-make)
- [Работа с базой данных](#работа-с-базой-данных)
- [Интеграции OpenAI и Google](#интеграции-openai-и-google)
- [Примечание по aiosqlite](#примечание-по-aiosqlite)
- [Лицензия](#лицензия)

## Возможности

- Асинхронный стек: FastAPI, SQLAlchemy, PostgreSQL/SQLite для тестов и локальной отладки.
- Интеграция с GPT для выбора и упорядочивания точек интереса.
- Поддержка Google Places и Distance Matrix (можно отключить).
- Проверка ограничений маршрута и сохранение черновиков.
- Docker/Compose для локального развёртывания.
- Тесты Pytest и линтеры Ruff/Black/Isort.

## Требования

- Python 3.10+ в среде WSL (Ubuntu 22.04+)
- `pip` и возможность создавать виртуальные окружения (`python -m venv`)
- Docker и Docker Compose (для развёртывания с PostgreSQL)

## Быстрая настройка окружения

1. Создайте виртуальное окружение в WSL и активируйте его (пример для Bash):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Установите зависимости из файла `.meta/packages`:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r ../.meta/packages
   ```
   > Аналогичные команды выполняет `make install`.
3. Создайте файл окружения. Можно оставить его в `city_guide/.env` или поместить в корне репозитория (`../.env`) — приложение найдёт оба варианта:
   ```bash
   cp .env.example .env
   ```
4. Для локальной отладки укажите SQLite, чтобы не поднимать инфраструктуру:
   ```dotenv
   DATABASE_URL=sqlite+aiosqlite:///./dev/cityguide.db
   ```
   Файл `city_guide/dev/cityguide.db` будет создан автоматически при первом запуске.

## Отладка в PyCharm

> Ниже приведён сценарий, проверенный на PyCharm 2024.1.

1. **Интерпретатор**. Откройте *Settings → Project → Python Interpreter* и нажмите *Add Interpreter → On WSL*. Выберите путь до интерпретатора вашего WSL-окружения (например, `<project>/.venv/bin/python`). Если окружение ещё не создано, PyCharm предложит сделать это автоматически.
2. **Sources Root**. В окне Project кликните правой кнопкой по папке `city_guide` → *Mark Directory as → Sources Root*. Это ускорит автодополнение и позволит IDE находить пакеты.
3. **ENV файл**. Убедитесь, что `.env` лежит либо в `city_guide/.env`, либо в корне репозитория (`../.env`). Переменная `CITY_GUIDE_ENV` не требуется — путь определяется автоматически.
4. **Run configuration**. Создайте конфигурацию типа *Python*:
   - *Module name*: `city_guide.app.debug`
   - *Working directory*: корень репозитория (`<project>/`)
   - *Python interpreter*: WSL-окружение из шага 1
   - *Environment variables*: при необходимости добавьте `PYTHONPATH=.` (необязательно, но удобно для пользовательских скриптов)
   - *Emulate terminal in output console*: **выключено** (иначе PyCharm запускает отдельный процесс, что мешает дебагу)

   Скрипт `city_guide/app/debug.py` запускает Uvicorn без горячей перезагрузки, поэтому брейкпоинты отрабатывают стабильно.

5. **Запуск**. Нажмите *Debug* в PyCharm. Сервис будет доступен на `http://localhost:8000`, Swagger UI — `/docs`.

## Запуск и команды Make

```bash
make install  # установка зависимостей через pip (.meta/packages)
make dev      # uvicorn с autoreload (для разработки вне дебага)
make run      # запуск uvicorn без autoreload (для продакшн-профиля)
make test     # юнит- и интеграционные тесты
make lint     # статический анализ и проверка форматирования
make format   # автоформатирование
```

Команды Make используют переменную `PYTHON` (по умолчанию `python3`) и автоматически добавляют корень репозитория в `PYTHONPATH`, чтобы пакеты `city_guide` и встроенный `aiosqlite` были доступны без дополнительной настройки.

## Работа с базой данных

- **PostgreSQL (рекомендуется для продакшена)**:
  1. Запустите инфраструктуру: `docker compose up -d`.
  2. Примените миграции: `make migrate`.
  3. Заполните тестовые данные: `make seed`.
- **SQLite (для тестов и отладки)**: дополнительная настройка не требуется. Миграции и сиды также применимы к SQLite.

## Интеграции OpenAI и Google

- Укажите `OPENAI_API_KEY` и `GPT_MODEL` для работы GPT-клиента.
- Для обращений к Google API задайте `GOOGLE_MAPS_API_KEY`. Переменная `USE_GOOGLE_SOURCES` отключает внешние запросы, оставляя генерацию маршрута на локальных заглушках.

## Примечание по aiosqlite

В репозитории присутствует облегчённая реализация `aiosqlite`, обеспечивающая работу SQLAlchemy в тестах без доступа к PyPI. При развёртывании с PostgreSQL она не задействуется.

## Лицензия

MIT

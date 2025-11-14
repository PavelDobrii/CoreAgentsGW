from __future__ import annotations

import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ..core.config import settings

_PARAM_PATTERN = re.compile(r":([a-zA-Z_][a-zA-Z0-9_]*)")
_BASE_DIR = Path(__file__).resolve().parents[2]


class Database:
    def __init__(self, url: str, testing: bool) -> None:
        self._url = url
        self._testing = testing
        self._parsed = urlparse(url)
        self._is_sqlite = self._parsed.scheme.startswith("sqlite")
        self._postgres_driver: Any | None = None
        if self._is_sqlite and self._parsed.path and self._parsed.path != ":memory:":
            self._ensure_sqlite_path()

    def _ensure_sqlite_path(self) -> None:
        if not self._parsed.path:
            return
        path = self._sqlite_path()
        os.makedirs(path.parent, exist_ok=True)

    def _sqlite_path(self) -> Path:
        raw = self._parsed.path
        if raw == ":memory:":
            return Path(raw)
        if raw.startswith("/"):
            path = Path(raw)
        else:
            path = (_BASE_DIR / raw.lstrip("/"))
        return path

    def _load_postgres_driver(self):
        if self._postgres_driver is not None:
            return self._postgres_driver
        for module_name in ("psycopg", "psycopg2"):
            try:
                module = __import__(module_name)
                self._postgres_driver = module
                return module
            except ModuleNotFoundError:
                continue
        raise RuntimeError("psycopg or psycopg2 must be installed to use PostgreSQL")

    def _prepare_sql(self, sql: str) -> str:
        if self._is_sqlite:
            return sql
        return _PARAM_PATTERN.sub(lambda match: f"%({match.group(1)})s", sql)

    def _connect_sqlite(self):
        path = self._sqlite_path()
        if str(path) == ":memory:":
            conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _connect_postgres(self):
        driver = self._load_postgres_driver()
        if driver.__name__ == "psycopg":
            return driver.connect(self._url, autocommit=False, row_factory=driver.rows.dict_row)
        return driver.connect(self._url)

    def _cursor_factory(self, connection):
        if self._is_sqlite:
            return connection.cursor()
        driver = self._load_postgres_driver()
        if driver.__name__ == "psycopg":
            return connection.cursor()
        return connection.cursor(cursor_factory=driver.extras.RealDictCursor)

    @contextmanager
    def _cursor(self):
        connection = self._connect_sqlite() if self._is_sqlite else self._connect_postgres()
        cursor = self._cursor_factory(connection)
        try:
            yield cursor
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def execute(self, sql: str, params: dict[str, Any] | None = None, *, fetchone: bool = False, fetchall: bool = False):
        prepared = self._prepare_sql(sql)
        with self._cursor() as cursor:
            cursor.execute(prepared, params or {})
            if fetchone:
                row = cursor.fetchone()
                return dict(row) if row is not None else None
            if fetchall:
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            return cursor.rowcount

    def reset(self) -> None:
        if not (self._testing and self._is_sqlite):
            return
        statements = [
            "DROP TABLE IF EXISTS route_points",
            "DROP TABLE IF EXISTS route_drafts",
            "DROP TABLE IF EXISTS user_profiles",
            "DROP TABLE IF EXISTS users",
            "CREATE TABLE IF NOT EXISTS users (\n                id TEXT PRIMARY KEY,\n                email TEXT NOT NULL UNIQUE,\n                password_hash TEXT NOT NULL,\n                first_name TEXT,\n                last_name TEXT,\n                phone TEXT,\n                country TEXT,\n                city TEXT,\n                language TEXT NOT NULL DEFAULT 'en',\n                is_active INTEGER NOT NULL DEFAULT 1,\n                created_at TEXT NOT NULL,\n                updated_at TEXT NOT NULL\n            )",
            "CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)",
            "CREATE TABLE IF NOT EXISTS user_profiles (\n                user_id TEXT PRIMARY KEY,\n                context TEXT NOT NULL,\n                updated_at TEXT NOT NULL\n            )",
            "CREATE TABLE IF NOT EXISTS route_drafts (\n                id TEXT PRIMARY KEY,\n                user_id TEXT NOT NULL,\n                city TEXT NOT NULL,\n                language TEXT NOT NULL,\n                duration_min INTEGER NOT NULL,\n                transport_mode TEXT NOT NULL,\n                status TEXT NOT NULL,\n                payload_json TEXT NOT NULL,\n                created_at TEXT NOT NULL,\n                updated_at TEXT NOT NULL\n            )",
            "CREATE INDEX IF NOT EXISTS ix_route_drafts_user_id ON route_drafts(user_id)",
            "CREATE TABLE IF NOT EXISTS route_points (\n                id TEXT PRIMARY KEY,\n                route_id TEXT NOT NULL,\n                poi_id TEXT NOT NULL,\n                name TEXT NOT NULL,\n                lat REAL NOT NULL,\n                lng REAL NOT NULL,\n                category TEXT NOT NULL,\n                order_index INTEGER NOT NULL,\n                eta_min_walk INTEGER,\n                eta_min_drive INTEGER,\n                listen_sec INTEGER,\n                source_poi_id TEXT\n            )",
            "CREATE INDEX IF NOT EXISTS ix_route_points_route_order ON route_points(route_id, order_index)",
        ]
        connection = self._connect_sqlite()
        try:
            cursor = connection.cursor()
            for statement in statements:
                cursor.execute(statement)
            connection.commit()
        finally:
            cursor.close()
            connection.close()


database = Database(settings.database_url, settings.testing)

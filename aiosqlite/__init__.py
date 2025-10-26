"""Упрощённая реализация aiosqlite для локального тестирования."""

from __future__ import annotations

import asyncio
import sqlite3
from contextlib import asynccontextmanager
from typing import Any, Iterable, Optional

__all__ = [
    "connect",
    "Connection",
    "Cursor",
    "Error",
    "OperationalError",
    "DatabaseError",
    "IntegrityError",
    "NotSupportedError",
    "ProgrammingError",
    "sqlite_version",
    "sqlite_version_info",
]

Error = sqlite3.Error
OperationalError = sqlite3.OperationalError
DatabaseError = sqlite3.DatabaseError
IntegrityError = sqlite3.IntegrityError
NotSupportedError = sqlite3.NotSupportedError
ProgrammingError = sqlite3.ProgrammingError
sqlite_version = sqlite3.sqlite_version
sqlite_version_info = sqlite3.sqlite_version_info


class Cursor:
    """Минимальный асинхронный курсор поверх стандартного sqlite3."""

    def __init__(self, connection: "Connection", cursor: sqlite3.Cursor) -> None:
        self._connection = connection
        self._cursor = cursor
        self.arraysize = 1
        self.rowcount = -1
        self.lastrowid: Optional[int] = None
        self.description = None

    async def execute(self, sql: str, parameters: Iterable[Any] | None = None) -> "Cursor":
        """Асинхронно выполняет SQL-запрос."""

        def _exec() -> sqlite3.Cursor:
            if parameters is None:
                return self._cursor.execute(sql)
            return self._cursor.execute(sql, tuple(parameters))

        await self._connection._run(_exec)
        self.description = self._cursor.description
        self.rowcount = self._cursor.rowcount if self._cursor.rowcount is not None else -1
        self.lastrowid = self._cursor.lastrowid
        return self

    async def executemany(self, sql: str, seq_of_parameters: Iterable[Iterable[Any]]) -> "Cursor":
        """Асинхронно выполняет набор SQL-запросов."""

        prepared = [tuple(params) for params in seq_of_parameters]
        await self._connection._run(self._cursor.executemany, sql, prepared)
        self.description = self._cursor.description
        self.rowcount = self._cursor.rowcount if self._cursor.rowcount is not None else -1
        self.lastrowid = self._cursor.lastrowid
        return self

    async def fetchone(self) -> Any:
        return await self._connection._run(self._cursor.fetchone)

    async def fetchmany(self, size: int | None = None) -> list[Any]:
        if size is None:
            size = self.arraysize
        return await self._connection._run(self._cursor.fetchmany, size)

    async def fetchall(self) -> list[Any]:
        return await self._connection._run(self._cursor.fetchall)

    async def close(self) -> None:
        await self._connection._run(self._cursor.close)

    async def __aenter__(self) -> "Cursor":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001, D401
        await self.close()


class Connection:
    """Асинхронная обёртка над sqlite3.Connection."""

    def __init__(self, inner: sqlite3.Connection) -> None:
        self._inner = inner
        self.row_factory = inner.row_factory

    async def _run(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        return await asyncio.to_thread(func, *args, **kwargs)

    async def cursor(self) -> Cursor:
        cursor = await self._run(self._inner.cursor)
        return Cursor(self, cursor)

    async def execute(self, sql: str, parameters: Iterable[Any] | None = None) -> Cursor:
        cursor = await self.cursor()
        await cursor.execute(sql, parameters)
        return cursor

    async def executemany(self, sql: str, seq_of_parameters: Iterable[Iterable[Any]]) -> Cursor:
        cursor = await self.cursor()
        await cursor.executemany(sql, seq_of_parameters)
        return cursor

    async def executescript(self, script: str) -> None:
        await self._run(self._inner.executescript, script)

    async def commit(self) -> None:
        await self._run(self._inner.commit)

    async def rollback(self) -> None:
        await self._run(self._inner.rollback)

    async def create_function(self, *args: Any, **kwargs: Any) -> None:
        await self._run(self._inner.create_function, *args, **kwargs)

    async def create_aggregate(self, *args: Any, **kwargs: Any) -> None:
        await self._run(self._inner.create_aggregate, *args, **kwargs)

    async def create_collation(self, *args: Any, **kwargs: Any) -> None:
        await self._run(self._inner.create_collation, *args, **kwargs)

    async def close(self) -> None:
        await self._run(self._inner.close)

    async def __aenter__(self) -> "Connection":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001, D401
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.close()

    @property
    def isolation_level(self) -> Optional[str]:
        return self._inner.isolation_level

    @isolation_level.setter
    def isolation_level(self, value: Optional[str]) -> None:
        self._inner.isolation_level = value

    def set_trace_callback(self, func: Any | None) -> None:
        self._inner.set_trace_callback(func)


class _ConnectAwaitable:
    """Объект, который ожидается для получения соединения."""

    def __init__(self, database: str, kwargs: dict[str, Any]) -> None:
        self._database = database
        self._kwargs = kwargs
        self.daemon = False  # SQLAlchemy ожидает этот атрибут

    async def _open(self) -> Connection:
        inner = await asyncio.to_thread(sqlite3.connect, self._database, **self._kwargs)
        return Connection(inner)

    def __await__(self):  # noqa: D401
        return self._open().__await__()


def connect(database: str, **kwargs: Any) -> _ConnectAwaitable:
    """Создаёт awaitable для подключения к SQLite."""

    kwargs.setdefault("check_same_thread", False)
    return _ConnectAwaitable(database, kwargs)


@asynccontextmanager
async def connect_ctx(database: str, **kwargs: Any):
    """Асинхронный контекстный менеджер для подключения (совместимость)."""

    conn = await connect(database, **kwargs)
    try:
        yield conn
    finally:
        await conn.close()

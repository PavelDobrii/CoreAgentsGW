"""A very small subset of the :mod:`pydantic` API used in the tests.

This repository purposely avoids pulling third-party dependencies from the
network during automated evaluation.  The real ``pydantic`` package is fairly
heavy-weight, but the application only relies on a handful of features:

* ``BaseModel`` for simple attribute containers.
* ``Field`` declarations with ``alias`` and ``default_factory`` support.
* ``ConfigDict`` placeholders on the models.
* ``EmailStr`` type hints.

The stub implemented below is intentionally tiny yet compatible with the
application code.  It performs basic required-field validation and provides a
``model_validate`` helper so GPT responses can still be parsed in tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict

__all__ = [
    "BaseModel",
    "ConfigDict",
    "EmailStr",
    "Field",
    "ValidationError",
]


class ValidationError(Exception):
    """Raised when instantiating a model with missing required fields."""


class _UnsetType:
    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - representation helper
        return "UNSET"


UNSET = _UnsetType()


@dataclass(slots=True)
class FieldInfo:
    default: Any = UNSET
    alias: str | None = None
    default_factory: Callable[[], Any] | None = None
    metadata: Dict[str, Any] | None = None


def Field(
    default: Any = UNSET,
    *,
    alias: str | None = None,
    default_factory: Callable[[], Any] | None = None,
    **metadata: Any,
) -> FieldInfo:
    """Return a lightweight container describing a model field."""

    if default is ...:
        default = UNSET
    if default is not UNSET and default_factory is not None:
        raise ValueError("`default` and `default_factory` are mutually exclusive")
    return FieldInfo(default=default, alias=alias, default_factory=default_factory, metadata=metadata)


def ConfigDict(**config: Any) -> Dict[str, Any]:
    """Pydantic 2 exposes ``ConfigDict``; here it is a thin dict wrapper."""

    return dict(config)


class EmailStr(str):
    """Simple alias used for type annotations."""


class BaseModel:
    """Extremely small subset of Pydantic's ``BaseModel`` implementation."""

    model_config: dict[str, Any] = {}

    def __init__(self, **data: Any) -> None:
        annotations = getattr(self.__class__, "__annotations__", {})
        remaining = dict(data)
        for name in annotations:
            field_info = getattr(self.__class__, name, UNSET)
            alias = None
            default = UNSET
            default_factory = None
            if isinstance(field_info, FieldInfo):
                alias = field_info.alias
                default = field_info.default
                default_factory = field_info.default_factory
            else:
                default = field_info

            key = None
            if alias and alias in remaining:
                key = alias
            elif name in remaining:
                key = name

            if key is not None:
                value = remaining.pop(key)
            else:
                if default is not UNSET:
                    value = default
                elif default_factory is not None:
                    value = default_factory()
                else:
                    raise ValidationError(f"Missing required field: {name}")

            setattr(self, name, value)

        for key, value in remaining.items():
            setattr(self, key, value)

    @classmethod
    def model_validate(cls, data: Any) -> "BaseModel":
        if isinstance(data, cls):
            return data
        if not isinstance(data, dict):
            raise ValidationError("Model validation requires a mapping")
        return cls(**data)

    def model_dump(self, *, by_alias: bool = False) -> dict[str, Any]:
        annotations = getattr(self.__class__, "__annotations__", {})
        result: dict[str, Any] = {}
        for name in annotations:
            field_info = getattr(self.__class__, name, UNSET)
            alias = field_info.alias if isinstance(field_info, FieldInfo) else None
            key = alias if alias and by_alias else name
            result[key] = getattr(self, name)
        return result

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        fields = getattr(self.__class__, "__annotations__", {})
        parts = ", ".join(f"{name}={getattr(self, name)!r}" for name in fields)
        return f"{self.__class__.__name__}({parts})"

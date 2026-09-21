"""Coerce Python values into what :func:`json.dumps` accepts."""

from __future__ import annotations

import dataclasses
import math
import pathlib
import sys
from collections.abc import Mapping
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID


def to_jsonable(obj: Any, *, nan: Any = None) -> Any:
    """Recursively convert *obj* into JSON-serialisable built-in types.

    Conversions:

    - ``dict``/mapping → ``dict`` with ``str`` keys; ``list``, ``tuple``,
      ``set`` and ``frozenset`` → ``list`` (sets are sorted when they can be,
      so the output is deterministic)
    - ``Enum`` → its ``value``; subclasses of ``str``/``int``/``float`` → the
      plain built-in
    - ``datetime``/``date``/``time`` → ISO 8601 text; ``timedelta`` → seconds
    - ``Decimal`` → ``float``; ``UUID`` and paths → ``str``
    - dataclass instances → ``dict`` of their fields
    - numpy scalars and arrays → Python scalars and nested lists (numpy is
      only consulted when it is already imported)
    - non-finite floats (``nan``, ``inf``) → *nan*, since JSON has no such value

    Can also be passed as ``default=`` to :func:`json.dumps`, where it is called
    only for values json cannot serialise itself.

    Args:
        obj: Value to convert.
        nan: Replacement for non-finite floats.

    Returns:
        A structure of ``dict``, ``list``, ``str``, ``int``, ``float``,
        ``bool`` and ``None``.

    Raises:
        TypeError: For a value with no known conversion.
    """
    if obj is None or isinstance(obj, bool):
        return obj
    if isinstance(obj, Enum):
        return to_jsonable(obj.value, nan=nan)
    if isinstance(obj, str):
        return str(obj)
    if isinstance(obj, int):
        return int(obj)
    if isinstance(obj, float):
        return float(obj) if math.isfinite(obj) else nan
    if isinstance(obj, Mapping):
        return {_key(k): to_jsonable(v, nan=nan) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v, nan=nan) for v in obj]
    if isinstance(obj, (set, frozenset)):
        items = [to_jsonable(v, nan=nan) for v in obj]
        try:
            return sorted(items)
        except TypeError:
            return items
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if isinstance(obj, timedelta):
        return obj.total_seconds()
    if isinstance(obj, Decimal):
        return to_jsonable(float(obj), nan=nan)
    if isinstance(obj, (UUID, pathlib.PurePath)):
        return str(obj)
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {
            f.name: to_jsonable(getattr(obj, f.name), nan=nan)
            for f in dataclasses.fields(obj)
        }
    np = sys.modules.get("numpy")
    if np is not None:
        if isinstance(obj, np.ndarray):
            return to_jsonable(obj.tolist(), nan=nan)
        if isinstance(obj, np.generic):
            return to_jsonable(obj.item(), nan=nan)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _key(key: Any) -> str:
    if isinstance(key, Enum):
        key = key.value
    return key if isinstance(key, str) else str(key)

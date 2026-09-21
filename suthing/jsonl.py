"""JSON Lines (``.jsonl`` / ``.ndjson``): one JSON value per line.

All functions accept compressed files (``.jsonl.gz`` etc., see :mod:`suthing.fs`).
Blank lines are skipped on read.
"""

from __future__ import annotations

import json
import logging
import pathlib
from collections.abc import Iterable, Iterator
from typing import IO, Any, NamedTuple

from suthing.fs import (
    PathLike,
    atomic_open,
    open_compressed,
    split_compression,
    wrap_compressed,
)
from suthing.jsonable import to_jsonable

logger = logging.getLogger(__name__)


class JsonlError(NamedTuple):
    """A line that could not be read.

    Attributes:
        line: 1-based line number.
        message: What was wrong with it.
    """

    line: int
    message: str

    def __str__(self) -> str:
        return f"line {self.line}: {self.message}"


def _parse(
    stream: IO[bytes], *, require_object: bool
) -> Iterator[tuple[int, Any, str | None]]:
    """Yield ``(line_no, value, error)`` for each non-blank line."""
    for line_no, raw in enumerate(stream, start=1):
        text = raw.strip()
        if not text:
            continue
        try:
            value = json.loads(text)
        except json.JSONDecodeError as e:
            yield line_no, None, f"not valid JSON ({e.msg})"
            continue
        if require_object and not isinstance(value, dict):
            yield line_no, None, f"expected a JSON object, got {type(value).__name__}"
            continue
        yield line_no, value, None


def iter_jsonl_stream(
    stream: IO[bytes], *, strict: bool = True, require_object: bool = False
) -> Iterator[Any]:
    """Parse JSON Lines from an open binary stream; see :func:`iter_jsonl`."""
    for line_no, value, error in _parse(stream, require_object=require_object):
        if error is None:
            yield value
        elif strict:
            raise ValueError(f"line {line_no}: {error}")
        else:
            logger.warning("skipping line %d: %s", line_no, error)


def iter_jsonl(
    path: PathLike, *, strict: bool = True, require_object: bool = False
) -> Iterator[Any]:
    """Stream the values of a JSON Lines file without loading it whole.

    Args:
        path: File to read; may be compressed.
        strict: Raise on a bad line. When ``False``, bad lines are logged at
            WARNING level and skipped.
        require_object: Treat any value that is not a JSON object as a bad line.

    Yields:
        One parsed value per non-blank line.

    Raises:
        ValueError: On a bad line when *strict* is set; the message carries the
            line number.
    """
    with open_compressed(path, "rb") as stream:
        yield from iter_jsonl_stream(
            stream, strict=strict, require_object=require_object
        )


def read_jsonl(
    path: PathLike, *, require_object: bool = False
) -> tuple[list[Any], list[JsonlError]]:
    """Read a whole JSON Lines file, collecting bad lines instead of raising.

    Args:
        path: File to read; may be compressed.
        require_object: Treat any value that is not a JSON object as a bad line.

    Returns:
        ``(rows, errors)``: the values that parsed, in file order, and one
        :class:`JsonlError` per line that did not.
    """
    rows: list[Any] = []
    errors: list[JsonlError] = []
    with open_compressed(path, "rb") as stream:
        for line_no, value, error in _parse(stream, require_object=require_object):
            if error is None:
                rows.append(value)
            else:
                errors.append(JsonlError(line_no, error))
    return rows, errors


def encode_jsonl_row(row: Any) -> bytes:
    """Encode one value as a UTF-8 JSON line, newline included.

    Non-ASCII text is written as-is and values json cannot serialise go through
    :func:`suthing.to_jsonable`.
    """
    return (json.dumps(row, ensure_ascii=False, default=to_jsonable) + "\n").encode(
        "utf-8"
    )


def write_jsonl_stream(rows: Iterable[Any], stream: IO[bytes]) -> int:
    """Write *rows* to an open binary stream; returns the number written."""
    if isinstance(rows, (str, bytes, dict)):
        raise TypeError(
            f"JSON Lines needs an iterable of rows, got {type(rows).__name__}"
        )
    count = 0
    for row in rows:
        stream.write(encode_jsonl_row(row))
        count += 1
    return count


def write_jsonl(
    rows: Iterable[Any],
    path: PathLike,
    *,
    append: bool = False,
    atomic: bool = True,
    mkdir: bool = False,
) -> int:
    """Write *rows* as JSON Lines, compressing by suffix.

    Args:
        rows: Values to write, one per line; any iterable, consumed once.
        path: Destination file.
        append: Add to the end of an existing file instead of replacing it.
            A compressed file gains a new compressed member, which every
            reader of that format accepts.
        atomic: Replace *path* in one step (see :func:`suthing.fs.atomic_open`).
            Ignored when appending.
        mkdir: Create missing parent directories first.

    Returns:
        The number of rows written.
    """
    dest = pathlib.Path(path).expanduser()
    if mkdir:
        dest.parent.mkdir(parents=True, exist_ok=True)
    if append or not atomic:
        with open_compressed(dest, "ab" if append else "wb") as stream:
            return write_jsonl_stream(rows, stream)
    _, compression = split_compression(dest)
    with atomic_open(dest) as raw:
        if compression is None:
            return write_jsonl_stream(rows, raw)
        with wrap_compressed(raw, compression, "wb") as stream:
            return write_jsonl_stream(rows, stream)

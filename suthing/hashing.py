"""Stable content hashes: of JSON-like values, text, bytes, files and directory trees.

Every function takes an ``algorithm`` name understood by :func:`hashlib.new`
(``"sha256"`` by default) and returns a hex digest.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from collections.abc import Callable
from typing import Any

from suthing.fs import PathLike

_CHUNK = 1 << 20


def _truncate(digest: str, length: int | None) -> str:
    if length is None:
        return digest
    if length < 1:
        raise ValueError(f"length must be positive, got {length}")
    return digest[:length]


def canonical_json(obj: Any, *, default: Callable[[Any], Any] | None = None) -> str:
    """Render *obj* as canonical JSON: sorted keys, no whitespace, ASCII-escaped.

    Equal values give identical text regardless of dict insertion order, which
    makes the result suitable for hashing and for use as a cache key.

    Args:
        obj: JSON-serialisable value.
        default: Hook for values json cannot serialise (e.g.
            :func:`suthing.to_jsonable`). Without it such values raise
            ``TypeError``, which keeps an accidental ``repr`` out of a hash.

    Returns:
        The canonical JSON text.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=default)


def bytes_hash(
    data: bytes, *, length: int | None = None, algorithm: str = "sha256"
) -> str:
    """Hex digest of *data*, optionally truncated to *length* characters."""
    return _truncate(hashlib.new(algorithm, data).hexdigest(), length)


def text_hash(
    text: str,
    *,
    length: int | None = None,
    algorithm: str = "sha256",
    encoding: str = "utf-8",
) -> str:
    """Hex digest of *text* encoded with *encoding*, optionally truncated."""
    return bytes_hash(text.encode(encoding), length=length, algorithm=algorithm)


def stable_hash(
    obj: Any,
    *,
    length: int | None = None,
    algorithm: str = "sha256",
    default: Callable[[Any], Any] | None = None,
) -> str:
    """Hex digest of :func:`canonical_json` of *obj*.

    Equal to ``hashlib.sha256(json.dumps(obj, sort_keys=True,
    separators=(",", ":")).encode("utf-8")).hexdigest()``, so it can replace
    that expression without changing any stored hash.

    Args:
        obj: JSON-serialisable value.
        length: Keep only the first *length* hex characters.
        algorithm: :mod:`hashlib` algorithm name.
        default: Passed to :func:`canonical_json`.

    Returns:
        The hex digest.
    """
    return text_hash(
        canonical_json(obj, default=default), length=length, algorithm=algorithm
    )


def file_hash(
    path: PathLike, *, length: int | None = None, algorithm: str = "sha256"
) -> str:
    """Hex digest of a file's raw bytes, read in chunks."""
    h = hashlib.new(algorithm)
    with open(pathlib.Path(path).expanduser(), "rb") as f:
        while chunk := f.read(_CHUNK):
            h.update(chunk)
    return _truncate(h.hexdigest(), length)


def tree_hash(
    root: PathLike,
    *,
    pattern: str = "*",
    length: int | None = None,
    algorithm: str = "sha256",
) -> str:
    """Hex digest of every file under *root* and its path relative to *root*.

    Files are visited in sorted order of their POSIX relative paths, so the
    result does not depend on the file system's listing order. Renaming or
    moving a file changes the hash; so does changing its contents. Directories
    and symlinks to directories contribute only through the files they hold.

    Args:
        root: Directory to hash.
        pattern: Glob matched recursively against file names (``rglob``).
        length: Keep only the first *length* hex characters.
        algorithm: :mod:`hashlib` algorithm name.

    Returns:
        The hex digest.

    Raises:
        NotADirectoryError: If *root* is not a directory.
    """
    base = pathlib.Path(root).expanduser()
    if not base.is_dir():
        raise NotADirectoryError(str(base))
    files = sorted(
        (p.relative_to(base).as_posix(), p) for p in base.rglob(pattern) if p.is_file()
    )
    h = hashlib.new(algorithm)
    for rel, p in files:
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(bytes.fromhex(file_hash(p, algorithm=algorithm)))
    return _truncate(h.hexdigest(), length)

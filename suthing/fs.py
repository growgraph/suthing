"""File-system primitives: path expansion, transparent compression, atomic writes.

Compression is chosen from the file name: ``.gz``, ``.bz2`` and ``.xz`` use the
standard library; ``.zst`` needs the optional ``zstandard`` package
(``pip install suthing[zstd]``).
"""

from __future__ import annotations

import bz2
import contextlib
import gzip
import io
import lzma
import os
import pathlib
import tempfile
from collections.abc import Callable, Iterator
from importlib import import_module
from typing import IO, Any, cast

PathLike = str | os.PathLike[str]

Opener = Callable[[Any, str], IO[bytes]]


def _gzip_open(fileobj: Any, mode: str) -> IO[bytes]:
    return cast(IO[bytes], gzip.GzipFile(fileobj=fileobj, mode=mode))


def _bz2_open(fileobj: Any, mode: str) -> IO[bytes]:
    # BZ2File types its mode as a literal; open_compressed has validated it.
    return cast(IO[bytes], bz2.BZ2File(fileobj, cast(Any, mode)))


def _xz_open(fileobj: Any, mode: str) -> IO[bytes]:
    return cast(IO[bytes], lzma.LZMAFile(fileobj, mode))


def _zstd_open(fileobj: Any, mode: str) -> IO[bytes]:
    try:
        zstandard = import_module("zstandard")
    except ImportError as e:  # pragma: no cover - depends on the environment
        raise ImportError(
            ".zst files need the optional 'zstandard' package:"
            " pip install 'suthing[zstd]'"
        ) from e
    stream = zstandard.open(fileobj, mode)
    if mode == "rb":
        # The zstandard reader has no readline(); buffering it restores line
        # iteration, which the JSONL and TXT readers rely on.
        return cast(IO[bytes], io.BufferedReader(stream))
    return stream


#: Compression suffix → function opening a binary stream over a file object.
COMPRESSORS: dict[str, Opener] = {
    ".gz": _gzip_open,
    ".bz2": _bz2_open,
    ".xz": _xz_open,
    ".zst": _zstd_open,
}


def expand_path(path: PathLike) -> pathlib.Path:
    """Expand ``~`` and make *path* absolute, resolving symlinks.

    Args:
        path: Path as a string or path-like object.

    Returns:
        The resolved absolute path.
    """
    return pathlib.Path(path).expanduser().resolve()


def split_compression(path: PathLike) -> tuple[str, str | None]:
    """Split a file name into its format suffix and compression suffix.

    The format suffix is the last extension once any compression suffix is
    removed. A dotfile such as ``.env`` counts as its own suffix.

    Args:
        path: File path or name.

    Returns:
        ``(format_suffix, compression_suffix)``, lower-cased; ``format_suffix``
        is ``""`` when there is none and ``compression_suffix`` is ``None`` for
        an uncompressed name.

    Example:
        >>> split_compression("data/rows.jsonl.gz")
        ('.jsonl', '.gz')
        >>> split_compression("config/.env")
        ('.env', None)
    """
    name = pathlib.PurePath(path).name.lower()
    compression = None
    for suffix in COMPRESSORS:
        if name.endswith(suffix) and len(name) > len(suffix):
            compression = suffix
            name = name[: -len(suffix)]
            break
    fmt = pathlib.PurePath(name).suffix
    if not fmt and name.startswith(".") and name.count(".") == 1:
        fmt = name
    return fmt, compression


@contextlib.contextmanager
def open_compressed(path: PathLike, mode: str = "rb") -> Iterator[IO[bytes]]:
    """Open *path* as a binary stream, decompressing or compressing by suffix.

    Args:
        path: File to open; ``~`` is expanded.
        mode: One of ``"rb"``, ``"wb"``, ``"ab"``.

    Yields:
        A binary file object.

    Raises:
        ValueError: If *mode* is not a binary read/write/append mode.
    """
    if mode not in ("rb", "wb", "ab"):
        raise ValueError(f"mode must be 'rb', 'wb' or 'ab', got {mode!r}")
    p = pathlib.Path(path).expanduser()
    _, compression = split_compression(p)
    with open(p, mode) as raw:
        if compression is None:
            yield raw
        else:
            with wrap_compressed(raw, compression, mode) as stream:
                yield stream


def wrap_compressed(fileobj: IO[bytes], compression: str, mode: str) -> IO[bytes]:
    """Wrap an open binary file object in a (de)compressing stream.

    Args:
        fileobj: Underlying binary file object.
        compression: A key of :data:`COMPRESSORS`, e.g. ``".gz"``.
        mode: ``"rb"``, ``"wb"`` or ``"ab"``.

    Returns:
        A binary stream over *fileobj*; close it before closing *fileobj* so
        compressed trailers get flushed.
    """
    return COMPRESSORS[compression](fileobj, mode)


def _default_file_mode() -> int:
    # os.umask is the only portable way to read the umask: set it and restore it.
    umask = os.umask(0)
    os.umask(umask)
    return 0o666 & ~umask


@contextlib.contextmanager
def atomic_open(
    path: PathLike, *, mkdir: bool = False, durable: bool = False
) -> Iterator[IO[bytes]]:
    """Open a binary stream whose contents replace *path* only on success.

    Data goes to a temporary file in the same directory, which is moved over
    *path* with :func:`os.replace` when the block exits without an exception.
    Readers therefore see either the old file or the complete new one, and
    concurrent writers never interleave (the last one to finish wins). On an
    exception the temporary file is removed and *path* is left untouched.

    The new file keeps the permissions of the file it replaces, or gets the
    usual ``0o666 & ~umask`` if *path* did not exist.

    Args:
        path: Destination file; ``~`` is expanded.
        mkdir: Create missing parent directories first.
        durable: ``fsync`` the data before the rename, so the new contents
            survive a crash, not just a concurrent reader.

    Yields:
        A binary file object to write to.
    """
    dest = pathlib.Path(path).expanduser()
    if mkdir:
        dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        mode = dest.stat().st_mode & 0o7777
    except FileNotFoundError:
        mode = _default_file_mode()
    fd, tmp_name = tempfile.mkstemp(
        dir=dest.parent, prefix=f".{dest.name}.", suffix=".tmp"
    )
    tmp = pathlib.Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as f:
            yield f
            f.flush()
            if durable:
                os.fsync(f.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, dest)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def atomic_write(
    path: PathLike,
    data: bytes | str,
    *,
    encoding: str = "utf-8",
    mkdir: bool = False,
    durable: bool = False,
) -> pathlib.Path:
    """Write *data* to *path* atomically (see :func:`atomic_open`).

    The data is written as-is: a ``.gz`` name is not compressed. Use
    :meth:`suthing.FileHandle.dump` for format- and compression-aware writes.

    Args:
        path: Destination file.
        data: Bytes, or text encoded with *encoding*.
        encoding: Encoding for text data.
        mkdir: Create missing parent directories first.
        durable: ``fsync`` before the rename.

    Returns:
        The destination path.
    """
    payload = data.encode(encoding) if isinstance(data, str) else data
    dest = pathlib.Path(path).expanduser()
    with atomic_open(dest, mkdir=mkdir, durable=durable) as f:
        f.write(payload)
    return dest

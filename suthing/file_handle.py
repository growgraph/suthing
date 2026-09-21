"""Read and write files whose format is inferred from the file name.

Supported formats are listed in :class:`FileType`; the extension → format map
is :data:`EXTENSIONS`. Any of them can be compressed with ``.gz``, ``.bz2``,
``.xz`` or ``.zst`` (see :mod:`suthing.fs`).
"""

from __future__ import annotations

import io
import json
import pathlib
import pickle
import warnings
from collections.abc import Iterator, Mapping
from enum import Enum
from importlib import resources
from typing import IO, Any

import yaml
from yaml.representer import RepresenterError

from suthing.fs import (
    PathLike,
    atomic_open,
    open_compressed,
    split_compression,
    wrap_compressed,
)
from suthing.jsonable import to_jsonable
from suthing.jsonl import iter_jsonl_stream, write_jsonl_stream


class FileType(str, Enum):
    """Formats :class:`FileHandle` reads and writes."""

    YAML = "yaml"
    JSON = "json"
    JSONL = "jsonl"
    PICKLE = "pkl"
    CSV = "csv"
    TSV = "tsv"
    TXT = "txt"
    ENV = "env"


#: File extension → format. ``.jsonld`` is JSON-LD, i.e. a JSON document.
EXTENSIONS: dict[str, FileType] = {
    ".yaml": FileType.YAML,
    ".yml": FileType.YAML,
    ".json": FileType.JSON,
    ".jsonld": FileType.JSON,
    ".jsonl": FileType.JSONL,
    ".ndjson": FileType.JSONL,
    ".pkl": FileType.PICKLE,
    ".pickle": FileType.PICKLE,
    ".csv": FileType.CSV,
    ".tsv": FileType.TSV,
    ".txt": FileType.TXT,
    ".md": FileType.TXT,
    ".env": FileType.ENV,
}


def detect_format(path: PathLike) -> tuple[FileType | None, str | None]:
    """Infer the format and compression of *path* from its name.

    Args:
        path: File path or name.

    Returns:
        ``(format, compression)``; ``format`` is ``None`` for an unknown
        extension and ``compression`` is ``None`` for an uncompressed file.
    """
    fmt, compression = split_compression(path)
    return EXTENSIONS.get(fmt), compression


def _resolve(path: PathLike, how: FileType | str | None) -> tuple[FileType, str | None]:
    detected, compression = detect_format(path)
    if how is not None:
        return FileType(how), compression
    if detected is None:
        raise ValueError(
            f"cannot infer the format of {str(path)!r} from its extension;"
            f" pass how=FileType.<X>. Known extensions: {', '.join(EXTENSIONS)}"
        )
    return detected, compression


class _Dumper(yaml.SafeDumper):
    """Safe YAML dumper that writes tuples as lists and coerces other types."""


def _represent_other(dumper: yaml.SafeDumper, data: Any) -> yaml.Node:
    converted = to_jsonable(data)
    if type(converted) is type(data):
        raise RepresenterError(
            f"cannot represent an object of type {type(data).__name__}"
        )
    return dumper.represent_data(converted)


_Dumper.add_representer(tuple, _Dumper.represent_list)
_Dumper.add_multi_representer(object, _represent_other)


def _no_kwargs(how: FileType, kwargs: Mapping[str, Any]) -> None:
    if kwargs:
        raise TypeError(
            f"unexpected keyword arguments for {how.name}: {', '.join(kwargs)}"
        )


def _read(stream: IO[bytes], how: FileType, **kwargs: Any) -> Any:
    if how in (FileType.CSV, FileType.TSV):
        import pandas as pd

        if how is FileType.TSV:
            kwargs.setdefault("sep", "\t")
        return pd.read_csv(stream, **kwargs)
    _no_kwargs(how, kwargs)
    if how is FileType.PICKLE:
        return pickle.load(stream)
    if how is FileType.YAML:
        return yaml.safe_load(stream)
    if how is FileType.JSON:
        return json.load(stream)
    if how is FileType.JSONL:
        return list(iter_jsonl_stream(stream))
    if how is FileType.TXT:
        return stream.read().decode("utf-8")
    if how is FileType.ENV:
        from dotenv import dotenv_values

        text = io.StringIO(stream.read().decode("utf-8"))
        return {k: v for k, v in dotenv_values(stream=text).items() if v is not None}
    raise AssertionError(f"unhandled format {how}")  # pragma: no cover


def _env_value(value: Any) -> str:
    text = str(value)
    if text and all(c.isalnum() or c in "._-/:@+,=" for c in text):
        return text
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def _encode(item: Any, how: FileType, **kwargs: Any) -> bytes:
    if how in (FileType.CSV, FileType.TSV):
        import pandas as pd

        if not isinstance(item, (pd.DataFrame, pd.Series)):
            raise TypeError(
                f"{how.name} output needs a pandas DataFrame or Series,"
                f" got {type(item).__name__}"
            )
        if how is FileType.TSV:
            kwargs.setdefault("sep", "\t")
        return item.to_csv(**kwargs).encode("utf-8")
    _no_kwargs(how, kwargs)
    if how is FileType.PICKLE:
        return pickle.dumps(item, pickle.HIGHEST_PROTOCOL)
    if how is FileType.YAML:
        text = yaml.dump(item, Dumper=_Dumper, sort_keys=False, allow_unicode=True)
        return text.encode("utf-8")
    if how is FileType.JSON:
        text = json.dumps(item, indent=2, ensure_ascii=False, default=to_jsonable)
        return (text + "\n").encode("utf-8")
    if how is FileType.TXT:
        if not isinstance(item, str):
            raise TypeError(f"TXT output needs a str, got {type(item).__name__}")
        return item.encode("utf-8")
    if how is FileType.ENV:
        if not isinstance(item, Mapping):
            raise TypeError(f"ENV output needs a mapping, got {type(item).__name__}")
        lines = [f"{k}={_env_value(v)}\n" for k, v in item.items()]
        return "".join(lines).encode("utf-8")
    raise AssertionError(f"unhandled format {how}")  # pragma: no cover


class FileHandle:
    """Format-aware file I/O: one call to read or write a whole file.

    The format comes from the extension (:data:`EXTENSIONS`) unless ``how`` is
    given, and a compression suffix is handled transparently. An unknown
    extension is an error rather than a guess.

    Formats read to / write from:

    - YAML, JSON (``.jsonld`` too): any YAML/JSON value. YAML loads with
      ``safe_load``; values json cannot serialise go through
      :func:`suthing.to_jsonable`.
    - JSONL: a list of values, one per line.
    - CSV, TSV: a pandas ``DataFrame`` (extra keyword arguments go to
      ``read_csv`` / ``to_csv``).
    - TXT: a ``str``.
    - ENV: a ``dict[str, str]``; loading does *not* touch ``os.environ``
      (use :func:`suthing.load_env` for that).
    - PICKLE: any picklable object. Only unpickle files you trust.

    Example:
        >>> data = FileHandle.load("config.yaml")
        >>> FileHandle.dump(data, "out/config.json.gz", mkdir=True)
    """

    @classmethod
    def load(
        cls,
        path: PathLike | None = None,
        *,
        how: FileType | str | None = None,
        fpath: PathLike | None = None,
        **kwargs: Any,
    ) -> Any:
        """Read a file from disk.

        Args:
            path: File to read; ``~`` is expanded.
            how: Format override; by default inferred from the extension.
            fpath: Deprecated spelling of *path*, kept so code written for
                suthing 0.5 keeps working; emits ``DeprecationWarning``.
            **kwargs: Passed to ``pandas.read_csv`` for CSV/TSV. Any other
                format rejects extra arguments.

        Returns:
            The parsed contents (see the class docstring for types).

        Raises:
            ValueError: If the format cannot be inferred.
            TypeError: For keyword arguments the format does not take, or
                when neither or both of *path* and *fpath* are given.
        """
        if fpath is not None:
            warnings.warn(
                "FileHandle.load(fpath=...) is deprecated; pass the path positionally",
                DeprecationWarning,
                stacklevel=2,
            )
            if path is not None:
                raise TypeError("pass the path once: positionally or as fpath=")
            path = fpath
        if path is None:
            raise TypeError("FileHandle.load() missing the file path")
        fmt, _ = _resolve(path, how)
        with open_compressed(path, "rb") as stream:
            return _read(stream, fmt, **kwargs)

    @classmethod
    def load_resource(
        cls,
        package: str,
        name: str,
        *,
        how: FileType | str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Read a data file shipped inside an importable package.

        Args:
            package: Dotted package name, e.g. ``"mypkg.data"``.
            name: File name relative to the package; may contain ``/``.
            how: Format override; by default inferred from the extension.
            **kwargs: As for :meth:`load`.

        Returns:
            The parsed contents.
        """
        fmt, compression = _resolve(name, how)
        data = resources.files(package).joinpath(name).read_bytes()
        with io.BytesIO(data) as raw:
            if compression is None:
                return _read(raw, fmt, **kwargs)
            with wrap_compressed(raw, compression, "rb") as stream:
                return _read(stream, fmt, **kwargs)

    @classmethod
    def iter(
        cls,
        path: PathLike,
        *,
        how: FileType | str | None = None,
        chunksize: int = 10_000,
        **kwargs: Any,
    ) -> Iterator[Any]:
        """Stream a file instead of loading it whole.

        Args:
            path: File to read.
            how: Format override; by default inferred from the extension.
            chunksize: Rows per ``DataFrame`` chunk for CSV/TSV.
            **kwargs: Passed to ``pandas.read_csv`` for CSV/TSV, and to
                :func:`suthing.jsonl.iter_jsonl_stream` (``strict``,
                ``require_object``) for JSONL.

        Yields:
            JSONL: one value per line. CSV/TSV: ``DataFrame`` chunks.
            TXT: lines without their trailing newline.

        Raises:
            ValueError: For a format that cannot be streamed.
        """
        fmt, _ = _resolve(path, how)
        if fmt not in (FileType.JSONL, FileType.CSV, FileType.TSV, FileType.TXT):
            raise ValueError(f"{fmt.name} files cannot be streamed; use load()")
        with open_compressed(path, "rb") as stream:
            if fmt is FileType.JSONL:
                yield from iter_jsonl_stream(stream, **kwargs)
            elif fmt is FileType.TXT:
                _no_kwargs(fmt, kwargs)
                for raw in stream:
                    yield raw.decode("utf-8").rstrip("\r\n")
            else:
                import pandas as pd

                if fmt is FileType.TSV:
                    kwargs.setdefault("sep", "\t")
                with pd.read_csv(stream, chunksize=chunksize, **kwargs) as reader:
                    yield from reader

    @classmethod
    def dump(
        cls,
        item: Any,
        path: PathLike,
        *,
        how: FileType | str | None = None,
        atomic: bool = True,
        mkdir: bool = False,
        **kwargs: Any,
    ) -> pathlib.Path:
        """Write *item* to a file, compressing by suffix.

        Args:
            item: Value to write (see the class docstring for accepted types).
            path: Destination; ``~`` is expanded.
            how: Format override; by default inferred from the extension.
            atomic: Replace *path* in one step, so readers never see a
                partial file (see :func:`suthing.fs.atomic_open`).
            mkdir: Create missing parent directories first.
            **kwargs: Passed to ``DataFrame.to_csv`` for CSV/TSV. Any other
                format rejects extra arguments.

        Returns:
            The path written.

        Raises:
            ValueError: If the format cannot be inferred.
            TypeError: If *item* does not fit the format, or for keyword
                arguments the format does not take.
        """
        fmt, compression = _resolve(path, how)
        dest = pathlib.Path(path).expanduser()
        if mkdir:
            dest.parent.mkdir(parents=True, exist_ok=True)
        if fmt is FileType.JSONL:
            _no_kwargs(fmt, kwargs)
            write = lambda stream: write_jsonl_stream(item, stream)
        else:
            # Encode first: a type error must not leave a truncated file behind.
            payload = _encode(item, fmt, **kwargs)
            write = lambda stream: stream.write(payload)

        if not atomic:
            with open_compressed(dest, "wb") as stream:
                write(stream)
            return dest
        with atomic_open(dest) as raw:
            if compression is None:
                write(raw)
            else:
                with wrap_compressed(raw, compression, "wb") as stream:
                    write(stream)
        return dest

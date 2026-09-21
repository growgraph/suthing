"""One-call logging configuration for scripts and CLIs."""

from __future__ import annotations

import logging
import logging.config
import pathlib
import sys
from typing import TextIO

from suthing.fs import PathLike

DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def setup_logging(
    level: int | str = "INFO",
    *,
    config: PathLike | None = None,
    fmt: str = DEFAULT_FORMAT,
    stream: TextIO | None = None,
    force: bool = False,
) -> None:
    """Configure the root logger, from a config file or with sensible defaults.

    With *config*, the file decides everything: ``.conf``/``.ini`` files go to
    :func:`logging.config.fileConfig` and ``.yaml``/``.yml``/``.json`` files
    to :func:`logging.config.dictConfig`. Loggers that already exist are kept
    enabled in both cases. Without *config*, :func:`logging.basicConfig` is
    called with *level*, *fmt* and *stream*.

    Args:
        level: Root level, as a number or a name such as ``"DEBUG"``.
        config: Optional logging config file.
        fmt: Format string when no *config* is given.
        stream: Output stream when no *config* is given (default ``stderr``).
        force: Replace handlers already attached to the root logger.

    Raises:
        FileNotFoundError: If *config* does not exist.
        ValueError: If *config* has an unsupported extension.
    """
    if config is None:
        logging.basicConfig(
            level=level, format=fmt, stream=stream or sys.stderr, force=force
        )
        return

    path = pathlib.Path(config).expanduser()
    if not path.is_file():
        raise FileNotFoundError(str(path))
    suffix = path.suffix.lower()
    if force:
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)
            handler.close()
    if suffix in (".conf", ".ini", ".cfg"):
        logging.config.fileConfig(path, disable_existing_loggers=False)
    elif suffix in (".yaml", ".yml", ".json"):
        from suthing.file_handle import FileHandle

        spec = FileHandle.load(path)
        if not isinstance(spec, dict):
            raise ValueError(f"{path} does not hold a logging config mapping")
        spec.setdefault("version", 1)
        spec.setdefault("disable_existing_loggers", False)
        logging.config.dictConfig(spec)
    else:
        raise ValueError(
            f"unsupported logging config {path.name!r}:"
            " expected .conf/.ini/.cfg or .yaml/.yml/.json"
        )

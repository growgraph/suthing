"""Environment variables: boolean flags and ``.env`` files."""

from __future__ import annotations

import os
import pathlib

from suthing.fs import PathLike

_TRUE = frozenset({"1", "true", "t", "yes", "y", "on"})
_FALSE = frozenset({"0", "false", "f", "no", "n", "off"})


def env_flag(name: str, default: bool = False) -> bool:
    """Read environment variable *name* as a boolean.

    ``1/true/t/yes/y/on`` are true and ``0/false/f/no/n/off`` are false,
    ignoring case and surrounding whitespace. Unset or empty gives *default*.

    Args:
        name: Variable name.
        default: Value when the variable is unset or empty.

    Returns:
        The flag value.

    Raises:
        ValueError: For any other value, so a typo does not silently read as
            *default*.
    """
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    if raw in _TRUE:
        return True
    if raw in _FALSE:
        return False
    raise ValueError(f"environment variable {name}={raw!r} is not a boolean")


def load_env(path: PathLike, *, override: bool = False) -> dict[str, str]:
    """Load a dotenv file into :data:`os.environ`.

    To read a dotenv file *without* touching the environment, use
    ``FileHandle.load(path)``, which returns its values as a dict.

    Args:
        path: Dotenv file.
        override: Replace variables that are already set. By default the
            existing environment wins.

    Returns:
        The variables the file defines (with values ``None`` in the file
        dropped).
    """
    from dotenv import dotenv_values, load_dotenv

    p = pathlib.Path(path).expanduser()
    if not p.is_file():
        raise FileNotFoundError(str(p))
    load_dotenv(p, override=override)
    return {k: v for k, v in dotenv_values(p).items() if v is not None}

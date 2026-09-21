"""Small useful things: format-aware file I/O, timing, profiling, deep diffs,
hashing and other helpers shared across projects."""

from importlib.metadata import version

from .compare import MISSING, Difference, diff, equals
from .environ import env_flag, load_env
from .file_handle import FileHandle, FileType
from .fs import atomic_open, atomic_write, expand_path, open_compressed
from .hashing import (
    bytes_hash,
    canonical_json,
    file_hash,
    stable_hash,
    text_hash,
    tree_hash,
)
from .iterx import batched
from .jsonable import to_jsonable
from .jsonl import JsonlError, iter_jsonl, read_jsonl, write_jsonl
from .log import setup_logging
from .profiling import Profiler, ProfileStats, active_profiler, profiled
from .text import slugify
from .timer import Timer, format_duration, utc_now_iso

__version__ = version(__name__)

__all__ = [
    "MISSING",
    "Difference",
    "FileHandle",
    "FileType",
    "JsonlError",
    "ProfileStats",
    "Profiler",
    "Timer",
    "active_profiler",
    "atomic_open",
    "atomic_write",
    "batched",
    "bytes_hash",
    "canonical_json",
    "diff",
    "env_flag",
    "equals",
    "expand_path",
    "file_hash",
    "format_duration",
    "iter_jsonl",
    "load_env",
    "open_compressed",
    "profiled",
    "read_jsonl",
    "setup_logging",
    "slugify",
    "stable_hash",
    "text_hash",
    "to_jsonable",
    "tree_hash",
    "utc_now_iso",
    "write_jsonl",
]

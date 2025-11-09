from importlib.metadata import version

from .compare import equals
from .decorate import Report, Return, SProfiler, profile, secureit, timeit
from .file_handle import FileHandle
from .timer import Timer

__version__ = version(__name__)


__all__ = [
    "Timer",
    "equals",
    "Report",
    "Return",
    "SProfiler",
    "profile",
    "secureit",
    "FileHandle",
]

from importlib.metadata import version

from suthing.connection.factory import ConfigFactory
from suthing.connection.onto import (
    ArangoConnectionConfig,
    ConnectionKind,
    DBConnectionConfig,
    Neo4jConnectionConfig,
    ProtoConnectionConfig,
    WSGIConfig,
)

from .compare import equals
from .decorate import Report, Return, SProfiler, profile, secureit, timeit
from .file_handle import FileHandle
from .timer import Timer

__version__ = version(__name__)


__all__ = [
    "ArangoConnectionConfig",
    "ConnectionKind",
    "DBConnectionConfig",
    "Neo4jConnectionConfig",
    "ProtoConnectionConfig",
    "WSGIConfig",
    "Timer",
    "equals",
    "Report",
    "Return",
    "SProfiler",
    "profile",
    "secureit",
]

"""Opt-in function profiling.

Decorate functions with :func:`profiled`; they are timed only while a
:class:`Profiler` is active, and cost one context-variable lookup otherwise::

    @profiled(key_args="batch_size")
    def ingest(rows, batch_size=100): ...

    with Profiler() as prof:
        ingest(rows, batch_size=50)
        ingest(rows, batch_size=500)
    prof.summary()  # {"ingest(batch_size=50)": ProfileStats(...), ...}

The active profiler lives in a :class:`contextvars.ContextVar`, so it follows
``async`` tasks. Threads start with no active profiler unless they run in a
copied context (``contextvars.copy_context().run``).
"""

from __future__ import annotations

import functools
import inspect
import statistics
from collections import defaultdict
from collections.abc import Callable, Sequence
from contextvars import ContextVar, Token
from time import perf_counter
from typing import Any, NamedTuple, ParamSpec, Self, TypeVar, overload

P = ParamSpec("P")
R = TypeVar("R")

_active: ContextVar[Profiler | None] = ContextVar("suthing_profiler", default=None)


class ProfileStats(NamedTuple):
    """Timing statistics for one profiling key, in seconds."""

    count: int
    total: float
    mean: float
    p50: float
    max: float


class Profiler:
    """Collects timings recorded by :func:`profiled` functions while active."""

    def __init__(self) -> None:
        self._samples: defaultdict[str, list[float]] = defaultdict(list)
        self._tokens: list[Token[Profiler | None]] = []

    def __enter__(self) -> Self:
        self._tokens.append(_active.set(self))
        return self

    def __exit__(self, *exc: object) -> None:
        _active.reset(self._tokens.pop())

    def record(self, key: str, seconds: float) -> None:
        """Add one timing under *key*."""
        self._samples[key].append(seconds)

    def samples(self) -> dict[str, list[float]]:
        """A copy of every recorded timing, by key."""
        return {k: list(v) for k, v in self._samples.items()}

    def summary(self) -> dict[str, ProfileStats]:
        """Count, total, mean, median and max timing per key."""
        return {
            k: ProfileStats(
                count=len(v),
                total=sum(v),
                mean=statistics.fmean(v),
                p50=statistics.median(v),
                max=max(v),
            )
            for k, v in self._samples.items()
        }

    def reset(self) -> None:
        """Drop all recorded timings."""
        self._samples.clear()


def active_profiler() -> Profiler | None:
    """The profiler recording in the current context, if any."""
    return _active.get()


def _key_builder(
    func: Callable[..., Any], name: str, key_args: Sequence[str]
) -> Callable[..., str]:
    if not key_args:
        return lambda *args, **kwargs: name
    signature = inspect.signature(func)
    unknown = [a for a in key_args if a not in signature.parameters]
    if unknown:
        raise ValueError(f"{name} has no parameter(s) {', '.join(unknown)}")

    def build(*args: Any, **kwargs: Any) -> str:
        try:
            bound = signature.bind(*args, **kwargs)
        except TypeError:
            return name
        bound.apply_defaults()
        parts = ",".join(f"{a}={bound.arguments.get(a)!r}" for a in key_args)
        return f"{name}({parts})"

    return build


@overload
def profiled(func: Callable[P, R], /) -> Callable[P, R]: ...


@overload
def profiled(
    *, key_args: str | Sequence[str] = (), name: str | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def profiled(
    func: Callable[P, R] | None = None,
    /,
    *,
    key_args: str | Sequence[str] = (),
    name: str | None = None,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Time calls to a function whenever a :class:`Profiler` is active.

    Usable bare (``@profiled``) or with options (``@profiled(key_args="x")``).

    Args:
        func: Function to wrap (bare use).
        key_args: Parameter name(s) whose values become part of the key, so
            calls with different arguments are reported separately
            (``"load(size=100)"``). Defaults are filled in.
        name: Key prefix; defaults to the function's qualified name.

    Returns:
        The wrapped function, or a decorator.

    Raises:
        ValueError: At decoration time, if a *key_args* name is not a
            parameter of the function.
    """
    args_tuple = (key_args,) if isinstance(key_args, str) else tuple(key_args)

    def decorate(f: Callable[P, R]) -> Callable[P, R]:
        label = name or getattr(f, "__qualname__", None) or repr(f)
        key_of = _key_builder(f, label, args_tuple)

        @functools.wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            prof = _active.get()
            if prof is None:
                return f(*args, **kwargs)
            start = perf_counter()
            try:
                return f(*args, **kwargs)
            finally:
                prof.record(key_of(*args, **kwargs), perf_counter() - start)

        return wrapper

    if func is not None:
        return decorate(func)
    return decorate

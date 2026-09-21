"""Wall-clock timing and timestamps."""

from __future__ import annotations

import logging
from collections.abc import Callable
from contextlib import ContextDecorator
from datetime import UTC, datetime
from time import perf_counter
from typing import Self

logger = logging.getLogger(__name__)

SECONDS_PER_MINUTE = 60


def format_duration(seconds: float, digits: int = 2) -> str:
    """Format a duration as ``"1 min 30.5 sec"`` (minutes only when non-zero).

    Args:
        seconds: Duration in seconds.
        digits: Decimal places for the seconds part.

    Returns:
        The formatted duration.
    """
    mins = int(seconds // SECONDS_PER_MINUTE)
    secs = round(seconds - mins * SECONDS_PER_MINUTE, digits)
    text = f"{secs} sec"
    return f"{mins} min {text}" if mins > 0 else text


def utc_now_iso(timespec: str = "seconds") -> str:
    """Current UTC time as ISO 8601 text, e.g. ``"2026-09-22T10:15:00+00:00"``.

    Args:
        timespec: Precision, as for :meth:`datetime.datetime.isoformat`
            (``"seconds"``, ``"milliseconds"``, ``"microseconds"``, ...).

    Returns:
        The timestamp, with an explicit ``+00:00`` offset.
    """
    return datetime.now(UTC).isoformat(timespec=timespec)


class Timer(ContextDecorator):
    """Measure the wall-clock time of a block or a function.

    Uses :func:`time.perf_counter`. ``elapsed`` is live inside the block and
    frozen once it exits. On exit the timer reports itself to *log* if given,
    otherwise logs at DEBUG level when it has a *label*.

    As a decorator (``@Timer("load")``) the same instance is re-entered on
    every call, so it reports the most recent call; it is not safe for
    recursive or concurrent calls of the decorated function.

    Example:
        >>> with Timer() as t:
        ...     do_work()
        >>> print(t.elapsed_str)
        >>> with Timer("ingest", log=print):
        ...     ingest()  # prints "ingest: 1.23 sec" on exit
    """

    def __init__(
        self, label: str | None = None, log: Callable[[str], object] | None = None
    ) -> None:
        """Create a timer.

        Args:
            label: Name used when reporting on exit.
            log: Called with ``"<label>: <duration>"`` on exit, e.g.
                ``logger.info`` or ``print``.
        """
        self.label = label
        self.log = log
        self._start: float | None = None
        self._end: float | None = None

    def __enter__(self) -> Self:
        self._start = perf_counter()
        self._end = None
        return self

    def __exit__(self, *exc: object) -> None:
        self._end = perf_counter()
        message = f"{self.label or 'elapsed'}: {self}"
        if self.log is not None:
            self.log(message)
        elif self.label is not None:
            logger.debug(message)

    @property
    def elapsed(self) -> float:
        """Seconds since entering; 0.0 if the timer never started."""
        if self._start is None:
            return 0.0
        end = self._end if self._end is not None else perf_counter()
        return end - self._start

    @property
    def elapsed_ms(self) -> int:
        """:attr:`elapsed` in whole milliseconds."""
        return int(self.elapsed * 1000)

    @property
    def running(self) -> bool:
        """Whether the timer has started and not yet exited."""
        return self._start is not None and self._end is None

    def format(self, digits: int = 2) -> str:
        """:attr:`elapsed` formatted by :func:`format_duration`."""
        return format_duration(self.elapsed, digits)

    @property
    def elapsed_str(self) -> str:
        """:attr:`elapsed` formatted with two decimals, e.g. ``"2 min 7.12 sec"``."""
        return self.format()

    def __str__(self) -> str:
        return self.format()

    def __repr__(self) -> str:
        state = "running" if self.running else f"elapsed={self.elapsed:.6f}"
        return f"Timer(label={self.label!r}, {state})"

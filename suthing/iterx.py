"""Iteration helpers."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from itertools import islice
from typing import TypeVar

T = TypeVar("T")


def batched(iterable: Iterable[T], n: int) -> Iterator[list[T]]:
    """Split *iterable* into consecutive lists of *n* items; the last may be shorter.

    Works on any iterable, including generators, and consumes it lazily.
    Unlike :func:`itertools.batched` (Python 3.12+) it yields lists, which
    callers can index, extend or pass straight to bulk-insert APIs.

    Args:
        iterable: Items to split.
        n: Batch size.

    Yields:
        Lists of at most *n* items.

    Raises:
        ValueError: If *n* is less than 1.

    Example:
        >>> list(batched(range(5), 2))
        [[0, 1], [2, 3], [4]]
    """
    if n < 1:
        raise ValueError(f"batch size must be at least 1, got {n}")
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch

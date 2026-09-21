"""Deep comparison of nested data, with the location of every difference."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from collections.abc import Set as AbstractSet
from numbers import Real
from typing import Any, NamedTuple


class _Missing:
    def __repr__(self) -> str:
        return "<missing>"


#: Stands in for the absent side of a :class:`Difference`.
MISSING: Any = _Missing()


class Difference(NamedTuple):
    """One place where two structures differ.

    Attributes:
        path: Where, e.g. ``$.users[1].name``.
        expected: The value on the expected side, or :data:`MISSING`.
        actual: The value on the actual side, or :data:`MISSING`.
        reason: Short description of the mismatch.
    """

    path: str
    expected: Any
    actual: Any
    reason: str

    def __str__(self) -> str:
        return (
            f"{self.path}: {self.reason}"
            f" (expected={self.expected!r}, actual={self.actual!r})"
        )


class _Enough(Exception):
    pass


def _child(path: str, key: Any) -> str:
    if isinstance(key, str) and key.isidentifier():
        return f"{path}.{key}"
    return f"{path}[{key!r}]"


def _is_container(x: Any) -> bool:
    return isinstance(x, Iterable) and not isinstance(x, (str, bytes, bytearray))


class _Differ:
    def __init__(
        self,
        rel_tol: float,
        abs_tol: float,
        ignore_order: bool,
        max_diffs: int | None,
    ) -> None:
        self.rel_tol = rel_tol
        self.abs_tol = abs_tol
        self.ignore_order = ignore_order
        self.max_diffs = max_diffs
        self.found: list[Difference] = []

    def add(self, path: str, expected: Any, actual: Any, reason: str) -> None:
        self.found.append(Difference(path, expected, actual, reason))
        if self.max_diffs is not None and len(self.found) >= self.max_diffs:
            raise _Enough

    def same(self, a: Any, b: Any) -> bool:
        sub = _Differ(self.rel_tol, self.abs_tol, self.ignore_order, 1)
        try:
            sub.walk(a, b, "$")
        except _Enough:
            return False
        return not sub.found

    def walk(self, e: Any, a: Any, path: str) -> None:
        if isinstance(e, Mapping) and isinstance(a, Mapping):
            self.mappings(e, a, path)
        elif isinstance(e, AbstractSet) and isinstance(a, AbstractSet):
            self.sets(e, a, path)
        elif _is_container(e) and _is_container(a):
            if not isinstance(e, Mapping) and not isinstance(a, Mapping):
                self.sequences(e, a, path)
            else:
                self.add(path, e, a, f"type {type(e).__name__} != {type(a).__name__}")
        else:
            self.scalars(e, a, path)

    def mappings(self, e: Mapping, a: Mapping, path: str) -> None:
        for k, v in e.items():
            if k in a:
                self.walk(v, a[k], _child(path, k))
            else:
                self.add(_child(path, k), v, MISSING, "missing key")
        for k, v in a.items():
            if k not in e:
                self.add(_child(path, k), MISSING, v, "unexpected key")

    def sets(self, e: AbstractSet, a: AbstractSet, path: str) -> None:
        for v in e - a:
            self.add(path, v, MISSING, "missing element")
        for v in a - e:
            self.add(path, MISSING, v, "unexpected element")

    def sequences(self, e: Iterable, a: Iterable, path: str) -> None:
        es = e if isinstance(e, Sequence) else list(e)
        as_ = a if isinstance(a, Sequence) else list(a)
        if self.ignore_order:
            self.unordered(es, as_, path)
            return
        for i in range(min(len(es), len(as_))):
            self.walk(es[i], as_[i], f"{path}[{i}]")
        for i in range(len(as_), len(es)):
            self.add(f"{path}[{i}]", es[i], MISSING, "missing item")
        for i in range(len(es), len(as_)):
            self.add(f"{path}[{i}]", MISSING, as_[i], "unexpected item")

    def unordered(self, es: Sequence, as_: Sequence, path: str) -> None:
        unmatched = list(range(len(as_)))
        for i, ev in enumerate(es):
            for j in unmatched:
                if self.same(ev, as_[j]):
                    unmatched.remove(j)
                    break
            else:
                self.add(f"{path}[{i}]", ev, MISSING, "no matching item")
        for j in unmatched:
            self.add(f"{path}[{j}]", MISSING, as_[j], "unexpected item")

    def scalars(self, e: Any, a: Any, path: str) -> None:
        if _is_number(e) and _is_number(a):
            if not self.numbers_match(e, a):
                self.add(path, e, a, "values differ")
            return
        try:
            equal = bool(e == a)
        except (TypeError, ValueError) as exc:  # e.g. an ambiguous array truth value
            self.add(path, e, a, f"cannot compare ({type(exc).__name__})")
            return
        if not equal:
            reason = (
                "values differ"
                if type(e) is type(a)
                else f"type {type(e).__name__} != {type(a).__name__}"
            )
            self.add(path, e, a, reason)

    def numbers_match(self, e: Any, a: Any) -> bool:
        fe, fa = float(e), float(a)
        if math.isnan(fe) or math.isnan(fa):
            return math.isnan(fe) and math.isnan(fa)
        if self.rel_tol == 0 and self.abs_tol == 0:
            return e == a
        return math.isclose(fe, fa, rel_tol=self.rel_tol, abs_tol=self.abs_tol)


def _is_number(x: Any) -> bool:
    return isinstance(x, Real) and not isinstance(x, bool)


def diff(
    expected: Any,
    actual: Any,
    *,
    rel_tol: float = 0.0,
    abs_tol: float = 0.0,
    ignore_order: bool = False,
    max_diffs: int | None = None,
) -> list[Difference]:
    """List every difference between two nested structures.

    Mappings are compared key by key; sets as sets; other non-string iterables
    (lists, tuples, generators, arrays) item by item, so a length mismatch is
    reported as missing or unexpected items. Everything else is compared with
    ``==``. Numbers of different types compare by value, ``nan`` equals
    ``nan``, and ``bool`` is not treated as a number.

    Args:
        expected: Reference value.
        actual: Value under test.
        rel_tol: Relative tolerance for numbers (:func:`math.isclose`).
        abs_tol: Absolute tolerance for numbers.
        ignore_order: Match sequence items regardless of position (as a
            multiset). Quadratic in sequence length.
        max_diffs: Stop after this many differences.

    Returns:
        The differences, empty when the structures match.

    Example:
        ```python
        for d in diff({"a": [1, 2]}, {"a": [1]}):
            print(d)
        # $.a[1]: missing item (expected=2, actual=<missing>)
        ```
    """
    differ = _Differ(rel_tol, abs_tol, ignore_order, max_diffs)
    try:
        differ.walk(expected, actual, "$")
    except _Enough:
        pass
    return differ.found


def equals(
    a: Any,
    b: Any,
    *,
    rel_tol: float = 0.0,
    abs_tol: float = 0.0,
    ignore_order: bool = False,
) -> bool:
    """Whether two nested structures match; see :func:`diff` for the rules.

    Stops at the first difference.
    """
    return not diff(
        a,
        b,
        rel_tol=rel_tol,
        abs_tol=abs_tol,
        ignore_order=ignore_order,
        max_diffs=1,
    )

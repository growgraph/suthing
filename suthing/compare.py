"""Utilities for comparing complex nested data structures."""

import logging
from collections.abc import Iterable
from typing import Any

logger = logging.getLogger(__name__)

excluded_types = (str, dict)


def equals(a: Any, b: Any) -> bool:
    """Deep comparison of two objects.

    Recursively compares nested dictionaries and iterables.
    Strings and dicts are treated as atomic values.

    Args:
        a: First object to compare
        b: Second object to compare

    Returns:
        True if objects are equal, False otherwise
    """
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            logger.error(f"a: {a.keys()} ; b: {b.keys()}")
            return False
        else:
            return all([equals(a[k], b[k]) for k in a.keys()])
    elif (isinstance(a, Iterable) and not isinstance(a, excluded_types)) and (
        isinstance(b, Iterable) and not isinstance(b, excluded_types)
    ):
        return all([equals(ea, eb) for ea, eb in zip(a, b)])
    else:
        return a == b

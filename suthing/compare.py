import logging
from collections.abc import Iterable

logger = logging.getLogger(__name__)


excluded_types = (str, dict)


def equals(a, b) -> bool:
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

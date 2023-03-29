from __future__ import annotations

import dataclasses
import functools
from typing import Any

from suthing.timer import Timer


@dataclasses.dataclass
class Return:
    ret: Any
    elapsed: float | None = None
    success: bool | None = None
    exception: Exception | None = None


def time_it(foo):
    @functools.wraps(foo)
    def wrapper(*args, **kwargs):
        with Timer() as timer:
            r = foo(*args, **kwargs)
        if isinstance(r, Return):
            r.elapsed = timer.elapsed
        else:
            r = Return(ret=r, elapsed=timer.elapsed)
        return r

    return wrapper


def secure_it(foo):
    @functools.wraps(foo)
    def wrapper(*args, **kwargs):
        try:
            r = foo(*args, **kwargs)
            if isinstance(r, Return):
                r.success = True
            else:
                r = Return(ret=r, success=True)
        except Exception as e:
            r = Return(ret=None, success=False, exception=e)
        return r

    return wrapper

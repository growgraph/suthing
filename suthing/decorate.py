from __future__ import annotations

import dataclasses
import functools
import hashlib
from typing import Any

from suthing.timer import Timer


@dataclasses.dataclass
class SimpleReturn:
    ret: Any
    elapsed: float | None = None
    success: bool | None = None
    exception: Exception | None = None


@dataclasses.dataclass
class Report:
    elapsed: float | None = None
    success: bool | None = None
    exception: Exception | None = None


@dataclasses.dataclass
class Return:
    ret: Any
    reports: dict[str, Report]


def hash_args(*args, **kwargs):
    m = hashlib.sha256()
    for arg in args:
        m.update(f"{arg}".encode("utf-8"))
    for key in sorted(kwargs.keys()):
        m.update(f"{kwargs[key]}".encode("utf-8"))
    return m.hexdigest()


def derive_hid(arg_name, *args, **kwargs):
    if arg_name is not None:
        if kwargs:
            extra = kwargs.get(arg_name, None)
        else:
            extra = args[0] if args else None
    else:
        extra = hash_args(*args, **kwargs)
    extra_str = str(extra)
    if len(extra_str) > 20:
        extra_str = extra_str[:8]
    return extra_str


def simple_timeit(foo):
    @functools.wraps(foo)
    def wrapper(*args, **kwargs):
        with Timer() as timer:
            r = foo(*args, **kwargs)
        if isinstance(r, Return):
            r.elapsed = timer.elapsed
        else:
            r = SimpleReturn(ret=r, elapsed=timer.elapsed)
        return r

    return wrapper


def simple_secureit(foo):
    @functools.wraps(foo)
    def wrapper(*args, **kwargs):
        try:
            r = foo(*args, **kwargs)
            if isinstance(r, Return):
                r.success = True
            else:
                r = SimpleReturn(ret=r, success=True)
        except Exception as e:
            r = SimpleReturn(ret=None, success=False, exception=e)
        return r

    return wrapper


def timeit(foo, arg_name=None):
    @functools.wraps(foo)
    def wrapper(*args, **kwargs):
        with Timer() as timer:
            r = foo(*args, **kwargs)
        extra_str = derive_hid(arg_name, *args, **kwargs)
        key = foo.__name__ + f"<{extra_str}>"
        report = Report(elapsed=timer.elapsed)
        if isinstance(r, Return):
            if key in r.reports:
                r.reports[key].elapsed = timer.elapsed
            else:
                r.reports = {f"{key}:{q}": w for q, w in r.reports.items()}
                r.reports[key] = report
                r.ret = r
        else:
            r = Return(ret=r, reports={key: Report(elapsed=timer.elapsed)})
        return r

    return wrapper


def secureit(foo, arg_name=None):
    @functools.wraps(foo)
    def wrapper(*args, **kwargs):
        extra_str = derive_hid(arg_name, *args, **kwargs)
        key = foo.__name__ + f"<{extra_str}>"
        try:
            r = foo(*args, **kwargs)
            if isinstance(r, Return):
                if key in r.reports:
                    r.reports[key].success = True
                else:
                    r.reports = {f"{key}:{q}": w for q, w in r.reports.items()}
                    r.reports[key] = Report(success=True)
                    r.ret = r
            else:
                r = Return(ret=r, reports={key: Report(success=True)})
        except Exception as e:
            r = Return(
                ret=None, reports={key: Report(success=False, exception=e)}
            )
        return r

    return wrapper

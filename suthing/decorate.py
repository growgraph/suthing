from __future__ import annotations

import dataclasses
import functools
import hashlib
from collections import defaultdict
from typing import Any

from suthing.timer import Timer


class SProfiler:
    def __init__(self):
        self.accumulator: defaultdict[str, list] = defaultdict(list)


@dataclasses.dataclass
class SimpleReturn:
    ret: Any
    elapsed: float | None = None
    success: bool | None = None
    exception: Exception | None = None


class Report:
    def __init__(self, *args, **kwargs):
        self.hkey: str = kwargs.pop("hkey", None)
        self.elapsed: float = kwargs.pop("elapsed", None)
        self.success: bool = kwargs.pop("success", None)
        self.exception: Exception = kwargs.pop("exception", None)

    def __repr__(self):
        s = ""
        for k, v in self.__dict__.items():
            s += f"{k} : {v.__repr__()} \n"
        return s


class Return(Report):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ret: Any = kwargs.pop("ret", None)
        self.reports: list[Report] = kwargs.pop("reports", [])

    def __repr__(self):
        s = ""
        for k, v in self.__dict__.items():
            s += f"{k} : {v.__repr__()} \n"
        return s

    def update(self, rets: list[Report]):
        for r in rets:
            self.reports += [Report(**r.__dict__)]


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
            extra = f"{arg_name}={extra}"
        else:
            extra = args[0] if args else None
            extra = str(extra)
    else:
        extra = hash_args(*args, **kwargs)
        if len(extra) > 20:
            extra = extra[:8]
    extra = f"({extra})"
    return extra


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
        hkey = foo.__name__ + f"<{extra_str}>"
        if isinstance(r, Return):
            r.elapsed = timer.elapsed
            if r.hkey is None:
                r.hkey = hkey
        else:
            r = Return(ret=r, hkey=hkey, elapsed=timer.elapsed)
        return r

    return wrapper


def secureit(foo, arg_name=None):
    @functools.wraps(foo)
    def wrapper(*args, **kwargs):
        extra_str = derive_hid(arg_name, *args, **kwargs)
        hkey = foo.__name__ + f"<{extra_str}>"
        try:
            r = foo(*args, **kwargs)
            if isinstance(r, Return):
                r.success = True
                if r.hkey is None:
                    r.hkey = hkey
            else:
                r = Return(ret=r, hkey=hkey, success=True)
        except Exception as e:
            r = Return(ret=None, hkey=hkey, success=False, exception=e)
        return r

    return wrapper


def profile(foo):
    @functools.wraps(foo)
    def wrapper(*args, **kwargs):
        _profiler = kwargs.pop("_profiler", None)
        if _profiler is not None and not isinstance(_profiler, SProfiler):
            raise TypeError(f"_profiler type should be SProfiler, got {type(_profiler)} instead")
        _arg_name = kwargs.pop("_arg_name", None)
        if _arg_name is not None and not isinstance(_arg_name, str):
            raise TypeError(f"_arg_name type should be str, got {type(_arg_name)} instead")
        if _profiler is not None:
            with Timer() as timer:
                r = foo(*args, **kwargs)

            extra_str = derive_hid(_arg_name, *args, **kwargs)
            hkey = foo.__name__ + f"{extra_str}"
            _profiler.accumulator[hkey] += [timer.elapsed]
        else:
            r = foo(*args, **kwargs)
        return r

    return wrapper

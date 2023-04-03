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


def derive_hid(arg_names, *args, **kwargs):
    if arg_names is not None:
        if kwargs:
            if isinstance(arg_names, list):
                extra = ",".join([f"{arg_names}={kwargs.get(a, None)}" for a in arg_names])
            elif isinstance(arg_names, str):
                extra = f"{arg_names}={kwargs.get(arg_names, None)}"
            else:
                raise TypeError(f"arg_names should be str or list of str, {type(arg_names)} provided")
        else:
            extra = f"{args[0]}"
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


def profile(_foo=None, _argnames=None):
    def wrapper(foo):
        @functools.wraps(foo)
        def decorate_with_timing(*args, **kwargs):
            _profiler = kwargs.get("_profiler", None)
            if _profiler is not None and not isinstance(_profiler, SProfiler):
                raise TypeError(f"_profiler type should be SProfiler, got {type(_profiler)} instead")
            if _argnames is not None and not isinstance(_argnames, str):
                raise TypeError(f"_arg_name type should be str, got {type(_argnames)} instead")
            if _profiler is not None:
                with Timer() as timer:
                    r = foo(*args, **kwargs)
                extra_str = derive_hid(_argnames, *args, **kwargs)
                hkey = foo.__name__ + f"{extra_str}"
                _profiler.accumulator[hkey] += [timer.elapsed]
            else:
                r = foo(*args, **kwargs)
            return r
        return decorate_with_timing
    if _foo is None:
        return wrapper
    else:
        return wrapper(_foo)

import pytest

from suthing import Profiler, active_profiler, profiled


@profiled(key_args="n")
def work(n, scale=1):
    return sum(range(n)) * scale


@profiled
def outer(ns):
    return [work(n) for n in ns]


def test_no_profiler_is_a_passthrough():
    assert active_profiler() is None
    assert work(3) == 3


def test_records_per_key_and_nesting():
    with Profiler() as prof:
        assert active_profiler() is prof
        outer([10, 10, 20])
        work(n=20, scale=2)
    assert active_profiler() is None
    summary = prof.summary()
    assert summary["work(n=10)"].count == 2
    assert summary["work(n=20)"].count == 2
    assert summary["outer"].count == 1
    stats = summary["work(n=10)"]
    assert stats.max >= stats.p50 > 0 and stats.total >= stats.mean


def test_multiple_key_args_and_defaults():
    @profiled(key_args=["n", "scale"], name="w")
    def w(n, scale=1):
        return n * scale

    with Profiler() as prof:
        w(2)
        w(2, scale=3)
    assert set(prof.samples()) == {"w(n=2,scale=1)", "w(n=2,scale=3)"}


def test_records_even_when_raising():
    @profiled
    def boom():
        raise RuntimeError

    with Profiler() as prof, pytest.raises(RuntimeError):
        boom()
    assert prof.summary()[boom.__qualname__].count == 1


def test_unknown_key_arg_fails_at_decoration():
    with pytest.raises(ValueError, match="no parameter"):

        @profiled(key_args="missing")
        def f(x):
            return x


def test_nested_profilers_restore_outer():
    with Profiler() as a:
        with Profiler() as b:
            work(1)
        work(1)
    assert b.summary()["work(n=1)"].count == 1
    assert a.summary()["work(n=1)"].count == 1
    a.reset()
    assert a.samples() == {}

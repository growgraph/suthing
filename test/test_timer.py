import time

from suthing import Timer, format_duration, utc_now_iso


def test_format_duration():
    assert format_duration(127.123) == "2 min 7.12 sec"
    assert format_duration(57.128) == "57.13 sec"
    assert format_duration(57.128, digits=1) == "57.1 sec"


def test_elapsed_is_live_then_frozen():
    t = Timer()
    assert t.elapsed == 0.0 and not t.running
    with t:
        time.sleep(0.01)
        inside = t.elapsed
        assert inside > 0 and t.running
    frozen = t.elapsed
    time.sleep(0.01)
    assert t.elapsed == frozen >= inside
    assert t.elapsed_ms == int(frozen * 1000)
    assert t.elapsed_str == t.format() == str(t)


def test_log_callback():
    messages = []
    with Timer("step", log=messages.append):
        pass
    assert len(messages) == 1 and messages[0].startswith("step: ")


def test_decorator():
    messages = []

    @Timer("f", log=messages.append)
    def f(x):
        return x + 1

    assert f(1) == 2 and f(2) == 3
    assert len(messages) == 2


def test_utc_now_iso():
    stamp = utc_now_iso()
    assert stamp.endswith("+00:00") and "." not in stamp
    assert "." in utc_now_iso("milliseconds")

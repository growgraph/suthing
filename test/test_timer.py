from suthing import Timer


def test_times_str():
    t = Timer()
    t.elapsed = 127.123
    assert t.elapsed_str == "2 min 7.12 sec"
    t.elapsed = 57.128
    assert t.elapsed_str == "57.13 sec"

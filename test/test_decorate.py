from suthing import secureit, timeit


def test_update():
    def a(x, extra=None):
        if extra is not None:
            x = x + extra
        return x + 2

    timed_a = timeit(a)
    print(timed_a(5))
    print(timed_a(4, extra=3))


def test_args():
    def a(x):
        return x + 2

    ta = timeit(a, "x")
    r = ta(4)
    assert "4" in r.hkey


def test_nested_pass():
    def a(x):
        return x + 2

    ta = timeit(a, "x")

    @timeit
    def top():
        r1 = ta(2)

        r2 = ta(3)

        # do something
        r3 = ta(r1.ret + r2.ret)
        r3.update([r1, r2, r3])

        return r3

    r = top()
    assert len(r.reports) == 3


def test_secure():
    def a(x):
        if x < 0:
            raise ValueError("x should be non negative")
        return x + 2

    fa = secureit(a)
    _ = fa(5)
    _ = fa(-1)


def test_combine():
    def a(x):
        if x < 0:
            raise ValueError("x should be non negative")
        return x + 2

    fa = timeit(secureit(a))
    r5 = fa(5)
    rneg1 = fa(-1)
    assert r5.success
    assert not rneg1.success

from suthing.decorate import SProfiler, profile


def test_profile():
    sp = SProfiler()

    @profile(_argnames="x")
    def a(x, **kwargs):
        r = [x**2 for x in range(x)]
        return r

    _ = a(x=100000, _profiler=sp)
    k = list(sp.view_stats().keys())[0]
    print(sp._accumulator)
    assert len(sp.view_stats()[k]) == 1


def test_profile_nested():
    sp = SProfiler()

    @profile(_argnames="x")
    def a(x, **kwargs):
        r = [x**2 for x in range(x)]
        return r

    @profile
    def b(r, **kwargs):
        for v in r:
            a(x=v, **kwargs)
        return r

    _ = b(r=[100000, 500, 10], _profiler=sp)
    _ = list(sp.view_stats().keys())[0]
    print(sp.view_stats())
    # assert len(sp.accumulator[k]) == 1

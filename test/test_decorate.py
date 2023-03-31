import unittest

from suthing import secureit, timeit


class TestDecorate(unittest.TestCase):
    def test_update(self):
        def a(x, extra=None):
            if extra is not None:
                x = x + extra
            return x + 2

        timed_a = timeit(a)
        print(timed_a(5))
        print(timed_a(4, extra=3))

    def test_nested(self):
        def a(x):
            return x + 2

        def b(x):
            x = a(x)
            return x * 3

        tb = timeit(b)
        r = tb(4)
        self.assertTrue("b<4b227777>" == next(iter(r.reports.keys())))

    def test_args(self):
        def a(x):
            return x + 2

        ta = timeit(a, "x")
        r = ta(4)
        self.assertTrue("4" in next(iter(r.reports.keys())))

    def test_nested_pass(self):
        def a(x):
            return x + 2

        ta = timeit(a, "x")

        @timeit
        def top():
            r1 = ta(2)

            r2 = ta(3)

            # do something
            r3 = ta(r1.ret + r2.ret)
            r3.reports.update({**r1.reports, **r2.reports})

            return r3

        r = top()
        self.assertEqual(len(r.reports), 4)

    def test_nested_pass_simple(self):
        def a(x):
            return x + 2

        ta = timeit(a, "x")

        def top():
            r1 = ta(2)

            r2 = ta(3)

            r3 = ta(r1.ret + r2.ret)
            r3.reports.update({**r1.reports, **r2.reports})

            return r3

        r = top()
        self.assertEqual(len(r.reports), 3)

    def test_secure(self):
        def a(x):
            if x < 0:
                raise ValueError("x should be non negative")
            return x + 2

        fa = secureit(a)
        print(fa(5))
        print(fa(-1))

    def test_combine(self):
        def a(x):
            if x < 0:
                raise ValueError("x should be non negative")
            return x + 2

        fa = timeit(secureit(a))
        r5 = fa(5)
        rneg1 = fa(-1)
        self.assertEqual(r5.reports["a<ef2d127d>"].success, True)
        self.assertEqual(rneg1.reports["a<1bad6b8c>"].success, False)

    def runTest(self):
        self.test_update()
        self.test_nested()
        self.test_args()
        self.test_nested_pass()
        self.test_nested_pass_simple()
        self.test_secure()
        self.test_combine()


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestDecorate())
    unittest.TextTestRunner(verbosity=2).run(suite)

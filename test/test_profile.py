import unittest

from suthing import Report, Return, secureit, timeit
from suthing.decorate import SProfiler, profile

class TestDecorate(unittest.TestCase):

    def test_profile(self):
        sp = SProfiler()

        @profile(_argnames="x")
        def a(x, **kwargs):
            r = [x**2 for x in range(x)]
            return r

        r = a(x=100000, _profiler=sp)
        k = list(sp.accumulator.keys())[0]
        print(sp.accumulator)
        self.assertEqual(len(sp.accumulator[k]), 1)


    def test_profile_nested(self):
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

        r = b(r=[100000, 500, 10], _profiler=sp)
        k = list(sp.accumulator.keys())[0]
        print(sp.accumulator)
        # self.assertEqual(len(sp.accumulator[k]), 1)

    def runTest(self):
        # self.test_profile()
        self.test_profile_nested()


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestDecorate())
    unittest.TextTestRunner(verbosity=2).run(suite)

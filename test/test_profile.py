import unittest

from suthing import Report, Return, secureit, timeit
from suthing.decorate import SProfiler, profile

sp = SProfiler()


class TestDecorate(unittest.TestCase):

    def test_profile(self):

        @profile
        def a(x):
            r = [x**2 for x in range(x)]
            return r

        r = a(x=100000, _profiler=sp, _arg_name="x")
        k = list(sp.accumulator.keys())[0]
        print(sp.accumulator)
        self.assertEqual(len(sp.accumulator[k]), 1)

    def runTest(self):
        self.test_profile()


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestDecorate())
    unittest.TextTestRunner(verbosity=2).run(suite)

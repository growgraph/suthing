import time
import unittest

from suthing import secure_it, time_it


class TestMPNNBlocks(unittest.TestCase):
    def test_update(self):
        def a(x):
            return x + 2

        timed_a = time_it(a)
        print(timed_a(5))

    def test_secure(self):
        def a(x):
            if x < 0:
                raise ValueError("x should be non negative")
            return x + 2

        fa = secure_it(a)
        print(fa(5))
        print(fa(-1))

    def runTest(self):
        self.test_update()
        self.test_secure()


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestMPNNBlocks())
    unittest.TextTestRunner(verbosity=2).run(suite)

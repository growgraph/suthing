import argparse
import os
import unittest
from pprint import pprint

from suthing.file_handle import FileHandle


class TestFH(unittest.TestCase):
    cpath = os.path.dirname(os.path.realpath(__file__))
    ref_json = [{"a": "abc"}, {"b": "abc"}]

    def __init__(self, reset):
        super().__init__()
        self.reset = reset

    def test_jsonld(self):
        path = os.path.join(self.cpath, f"./data/example.jsonld")
        r = FileHandle.load("jsonld", fpath=path)
        self.assertEqual(self.ref_json, r)

    def test_jsonldgz(self):
        path = os.path.join(self.cpath, f"./data/example.jsonld.gz")
        r = FileHandle.load("jsonld", fpath=path)
        self.assertEqual(self.ref_json, r)

    def test_dump(self):
        path = os.path.join(self.cpath, f"./data/example.jsonld.gz")
        FileHandle.dump(self.ref_json, path)
        path = os.path.join(self.cpath, f"./data/example.jsonld")
        FileHandle.dump(self.ref_json, path)

    def runTest(self):
        self.test_jsonld()
        self.test_jsonldgz()
        self.test_dump()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reset", action="store_true", help="reset test results"
    )
    args = parser.parse_args()
    suite = unittest.TestSuite()
    suite.addTest(TestFH(args.reset))
    unittest.TextTestRunner(verbosity=2).run(suite)

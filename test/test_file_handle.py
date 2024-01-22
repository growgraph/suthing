import os

import pandas as pd
import pytest

from suthing.file_handle import FileHandle


@pytest.fixture()
def parameters():
    cpath = os.path.dirname(os.path.realpath(__file__))
    ref_json = [{"a": "abc"}, {"b": "abc"}]
    return [cpath, ref_json]


def test_env(parameters):
    cpath, rj = parameters
    path = os.path.join(cpath, "./data/example.env")
    _ = FileHandle.load(path)
    port = os.getenv("ARANGO_PORT")
    assert port == "8535"


def test_jsonld(parameters):
    cpath, rj = parameters
    path = os.path.join(cpath, "./data/example.jsonld")
    r = FileHandle.load("jsonld", fpath=path)
    assert rj == r


def test_jsonldgz(parameters):
    cpath, rj = parameters
    path = os.path.join(cpath, "./data/example.jsonld.gz")
    r = FileHandle.load("jsonld", fpath=path)
    assert rj == r


def test_dump(parameters):
    cpath, ref_json = parameters
    path = os.path.join(cpath, "./data/example.jsonld.gz")
    FileHandle.dump(ref_json, path)
    path = os.path.join(cpath, "./data/example.jsonld")
    FileHandle.dump(ref_json, path)


def test_csv_dump(parameters):
    cpath, rj = parameters
    df = pd.DataFrame([[1, 1, 1]], columns=["a", "b", "c"])
    path = os.path.join(cpath, "./data/example.csv")
    FileHandle.dump(df, path)


def test_txt():
    r = FileHandle.load("test.data", "some.secret")
    assert r == "123"

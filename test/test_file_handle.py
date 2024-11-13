import os

import pandas as pd

from suthing.file_handle import FileHandle


def test_env(parameters):
    cpath, rj = parameters
    path = os.path.join(cpath, "./data/example.env")
    _ = FileHandle.load(path)
    port = os.getenv("ARANGO_PORT")
    assert port == "8535"


def test_env_raw(parameters):
    cpath, rj = parameters
    path = os.path.join(cpath, "./data/.env")
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

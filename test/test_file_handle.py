import gzip
import os
import pathlib
import stat
from datetime import date
from enum import Enum

import pandas as pd
import pytest

from suthing import FileHandle, FileType
from suthing.file_handle import detect_format

COMPRESSIONS = ["", ".gz", ".bz2", ".xz"]


class Color(str, Enum):
    RED = "red"


@pytest.mark.parametrize("compression", COMPRESSIONS)
@pytest.mark.parametrize(
    "ext, item",
    [
        (".yaml", {"b": [1, 2], "a": {"x": "é"}}),
        (".json", {"b": [1, 2], "a": {"x": "é"}}),
        (".jsonl", [{"a": 1}, {"b": "é"}]),
        (".pkl", {"a": (1, 2), "b": {3}}),
        (".txt", "line one\nligne deux é\n"),
    ],
)
def test_round_trip(tmp_path, ext, compression, item):
    path = tmp_path / f"f{ext}{compression}"
    written = FileHandle.dump(item, path)
    assert written == path
    assert FileHandle.load(path) == item


def test_text_into_gzip(tmp_path):
    # 0.5.x raised TypeError writing str into a GzipFile.
    path = tmp_path / "note.txt.gz"
    FileHandle.dump("hi", path)
    assert gzip.decompress(path.read_bytes()) == b"hi"


def test_csv_round_trip(tmp_path):
    df = pd.DataFrame([[1, 2, 3]], columns=["a", "b", "c"])
    path = tmp_path / "t.csv.gz"
    FileHandle.dump(df, path, index=False)
    pd.testing.assert_frame_equal(FileHandle.load(path), df)


def test_tsv_uses_tabs(tmp_path):
    df = pd.DataFrame([[1, 2]], columns=["a", "b"])
    path = FileHandle.dump(df, tmp_path / "t.tsv", index=False)
    assert path.read_text() == "a\tb\n1\t2\n"
    pd.testing.assert_frame_equal(FileHandle.load(path), df)


def test_reads_tracked_fixtures(data_dir, rows):
    assert FileHandle.load(data_dir / "example.jsonl") == rows
    assert FileHandle.load(data_dir / "example.jsonl.gz") == rows
    assert list(FileHandle.load(data_dir / "example.csv", index_col=0).columns) == [
        "a",
        "b",
        "c",
    ]


def test_unknown_extension_raises(tmp_path):
    with pytest.raises(ValueError, match="cannot infer"):
        FileHandle.dump({"a": 1}, tmp_path / "x.unknownext")
    assert not (tmp_path / "x.unknownext").exists()


def test_how_overrides_extension(tmp_path):
    path = tmp_path / "config.conf"
    FileHandle.dump({"a": 1}, path, how=FileType.YAML)
    assert FileHandle.load(path, how="yaml") == {"a": 1}
    # the override wins over a known extension too
    FileHandle.dump({"a": 1}, tmp_path / "x.txt", how=FileType.JSON)
    assert FileHandle.load(tmp_path / "x.txt", how=FileType.JSON) == {"a": 1}


@pytest.mark.parametrize(
    "item, name",
    [([1, 2], "x.csv"), ({"a": 1}, "x.txt"), ([1], "x.env"), ({"a": 1}, "x.jsonl")],
)
def test_type_mismatch_raises_and_writes_nothing(tmp_path, item, name):
    with pytest.raises(TypeError):
        FileHandle.dump(item, tmp_path / name)
    assert list(tmp_path.iterdir()) == []


def test_unexpected_kwargs_rejected(tmp_path):
    path = FileHandle.dump({"a": 1}, tmp_path / "x.yaml")
    with pytest.raises(TypeError, match="sep"):
        FileHandle.load(path, sep=",")


def test_deprecated_fpath_still_loads(tmp_path):
    path = FileHandle.dump({"a": 1}, tmp_path / "x.yaml")
    with pytest.warns(DeprecationWarning, match="fpath"):
        assert FileHandle.load(fpath=path) == {"a": 1}
    with pytest.raises(TypeError, match="once"), pytest.warns(DeprecationWarning):
        FileHandle.load(path, fpath=path)
    with pytest.raises(TypeError, match="missing"):
        FileHandle.load()


def test_jsonld_is_json_ld(tmp_path):
    doc = {"@context": {"name": "http://schema.org/name"}, "name": "x"}
    path = tmp_path / "doc.jsonld"
    FileHandle.dump(doc, path)
    assert path.read_text().startswith("{\n")
    assert FileHandle.load(path) == doc


def test_yaml_keeps_order_unicode_and_coerces_types(tmp_path):
    item = {"z": Color.RED, "a": (1, 2), "d": date(2026, 1, 2), "u": "é"}
    path = FileHandle.dump(item, tmp_path / "x.yaml")
    text = path.read_text(encoding="utf-8")
    assert text.index("z:") < text.index("a:")
    assert "é" in text and "!!python" not in text
    assert FileHandle.load(path) == {
        "z": "red",
        "a": [1, 2],
        "d": date(2026, 1, 2),
        "u": "é",
    }


def test_yaml_load_is_safe(tmp_path):
    path = tmp_path / "x.yaml"
    path.write_text("!!python/object/apply:os.getcwd []\n")
    with pytest.raises(Exception, match="constructor"):
        FileHandle.load(path)


def test_json_uses_to_jsonable(tmp_path):
    path = FileHandle.dump(
        {"c": Color.RED, "p": pathlib.Path("/x")}, tmp_path / "a.json"
    )
    assert FileHandle.load(path) == {"c": "red", "p": "/x"}


def test_env_load_does_not_touch_environ(tmp_path, monkeypatch):
    monkeypatch.delenv("SUTHING_TEST_PORT", raising=False)
    path = tmp_path / "sample.env"
    FileHandle.dump({"SUTHING_TEST_PORT": "8535", "NAME": "a b"}, path)
    assert FileHandle.load(path) == {"SUTHING_TEST_PORT": "8535", "NAME": "a b"}
    assert "SUTHING_TEST_PORT" not in os.environ


def test_load_resource(rows):
    assert FileHandle.load_resource("test.data", "example.jsonl") == rows
    assert FileHandle.load_resource("test.data", "example.jsonl.gz") == rows
    assert FileHandle.load_resource("test.data", "some.secret", how="txt") == "123"


def test_mkdir(tmp_path):
    path = tmp_path / "a" / "b" / "x.json"
    with pytest.raises(FileNotFoundError):
        FileHandle.dump({}, path)
    FileHandle.dump({}, path, mkdir=True)
    assert FileHandle.load(path) == {}


@pytest.mark.parametrize("atomic", [True, False])
def test_dump_replaces_existing_file(tmp_path, atomic):
    path = tmp_path / "x.json"
    FileHandle.dump({"v": 1}, path, atomic=atomic)
    FileHandle.dump({"v": 2}, path, atomic=atomic)
    assert FileHandle.load(path) == {"v": 2}
    assert [p.name for p in tmp_path.iterdir()] == ["x.json"]


def test_atomic_dump_failure_keeps_original(tmp_path):
    path = FileHandle.dump([{"v": 1}], tmp_path / "x.jsonl")

    def rows():
        yield {"v": 2}
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        FileHandle.dump(rows(), path)
    assert FileHandle.load(path) == [{"v": 1}]
    assert [p.name for p in tmp_path.iterdir()] == ["x.jsonl"]


def test_atomic_dump_keeps_permissions(tmp_path):
    path = FileHandle.dump({"v": 1}, tmp_path / "x.json")
    path.chmod(0o640)
    FileHandle.dump({"v": 2}, path)
    assert stat.S_IMODE(path.stat().st_mode) == 0o640


def test_iter(tmp_path):
    FileHandle.dump([{"i": i} for i in range(5)], tmp_path / "x.jsonl.gz")
    assert [r["i"] for r in FileHandle.iter(tmp_path / "x.jsonl.gz")] == list(range(5))

    FileHandle.dump("a\nb\n", tmp_path / "x.txt")
    assert list(FileHandle.iter(tmp_path / "x.txt")) == ["a", "b"]

    df = pd.DataFrame({"a": range(5)})
    FileHandle.dump(df, tmp_path / "x.csv", index=False)
    chunks = list(FileHandle.iter(tmp_path / "x.csv", chunksize=2))
    assert [len(c) for c in chunks] == [2, 2, 1]

    with pytest.raises(ValueError, match="cannot be streamed"):
        list(FileHandle.iter(tmp_path / "x.csv", how="json"))


@pytest.mark.parametrize(
    "name, expected",
    [
        ("a.yml", (FileType.YAML, None)),
        ("a.tar.json.gz", (FileType.JSON, ".gz")),
        ("A.JSONL.XZ", (FileType.JSONL, ".xz")),
        ("dir/.env", (FileType.ENV, None)),
        ("x.gz", (None, ".gz")),
        ("noext", (None, None)),
    ],
)
def test_detect_format(name, expected):
    assert detect_format(name) == expected


def test_zstd_round_trip(tmp_path):
    pytest.importorskip("zstandard")
    FileHandle.dump([{"i": 1}, {"i": 2}], tmp_path / "x.jsonl.zst")
    assert list(FileHandle.iter(tmp_path / "x.jsonl.zst")) == [{"i": 1}, {"i": 2}]

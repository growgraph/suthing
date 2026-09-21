import gzip

import pytest

from suthing import JsonlError, iter_jsonl, read_jsonl, write_jsonl


@pytest.mark.parametrize("name", ["x.jsonl", "x.jsonl.gz", "x.ndjson.bz2"])
def test_round_trip(tmp_path, name):
    rows = [{"a": 1}, {"b": "é"}, [1, 2], 3]
    assert write_jsonl(iter(rows), tmp_path / name) == 4
    assert list(iter_jsonl(tmp_path / name)) == rows


def test_append_gz(tmp_path):
    path = tmp_path / "x.jsonl.gz"
    write_jsonl([{"i": 0}], path)
    write_jsonl([{"i": 1}], path, append=True)
    assert [r["i"] for r in iter_jsonl(path)] == [0, 1]
    assert gzip.decompress(path.read_bytes()).count(b"\n") == 2


def test_writes_utf8_unescaped(tmp_path):
    path = tmp_path / "x.jsonl"
    write_jsonl([{"t": "é"}], path)
    assert path.read_text(encoding="utf-8") == '{"t": "é"}\n'


def _bad_file(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text('{"a": 1}\n\nnot json\n[1]\n{"b": 2}\n')
    return path


def test_strict_reports_line_number(tmp_path):
    with pytest.raises(ValueError, match="line 3: not valid JSON"):
        list(iter_jsonl(_bad_file(tmp_path)))


def test_non_strict_skips(tmp_path):
    rows = list(iter_jsonl(_bad_file(tmp_path), strict=False, require_object=True))
    assert rows == [{"a": 1}, {"b": 2}]


def test_read_jsonl_collects_errors(tmp_path):
    rows, errors = read_jsonl(_bad_file(tmp_path), require_object=True)
    assert rows == [{"a": 1}, {"b": 2}]
    assert [e.line for e in errors] == [3, 4]
    assert str(errors[1]) == "line 4: expected a JSON object, got list"
    assert isinstance(errors[0], JsonlError)


def test_rejects_single_mapping(tmp_path):
    with pytest.raises(TypeError):
        write_jsonl({"a": 1}, tmp_path / "x.jsonl")

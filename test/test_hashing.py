import hashlib
import json

import pytest

from suthing import (
    bytes_hash,
    canonical_json,
    file_hash,
    stable_hash,
    text_hash,
    tree_hash,
)

PAYLOADS = [
    {"b": 1, "a": [1, 2, {"z": None, "y": "é"}]},
    {"canon": 1, "payload": {"ops": [], "parents": ["abc"]}},
    [],
    "text",
]


@pytest.mark.parametrize("payload", PAYLOADS)
def test_stable_hash_matches_the_inline_idiom(payload):
    # stable_hash must be a drop-in for this expression: stored hashes built
    # with it must not change when callers switch.
    inline = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert stable_hash(payload) == inline
    assert stable_hash(payload, length=12) == inline[:12]


def test_canonical_json_ignores_key_order():
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_canonical_json_rejects_unknown_types_by_default():
    with pytest.raises(TypeError):
        canonical_json({"s": {1}})
    assert canonical_json({"s": {1}}, default=list) == '{"s":[1]}'


def test_text_and_bytes_hash():
    assert text_hash("abc") == hashlib.sha256(b"abc").hexdigest()
    assert bytes_hash(b"abc", algorithm="md5") == hashlib.md5(b"abc").hexdigest()
    assert len(text_hash("abc", length=8)) == 8
    with pytest.raises(ValueError):
        text_hash("abc", length=0)


def test_file_and_tree_hash(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.txt").write_bytes(b"one")
    (tmp_path / "sub" / "b.txt").write_bytes(b"two")
    assert file_hash(tmp_path / "a.txt") == hashlib.sha256(b"one").hexdigest()

    first = tree_hash(tmp_path)
    assert tree_hash(tmp_path) == first
    (tmp_path / "sub" / "b.txt").rename(tmp_path / "sub" / "c.txt")
    renamed = tree_hash(tmp_path)
    assert renamed != first
    (tmp_path / "sub" / "c.txt").write_bytes(b"three")
    assert tree_hash(tmp_path) != renamed
    assert tree_hash(tmp_path, pattern="a.txt") != tree_hash(tmp_path)
    with pytest.raises(NotADirectoryError):
        tree_hash(tmp_path / "a.txt")

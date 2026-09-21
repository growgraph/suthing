import dataclasses
import logging
import math
import os
import pathlib
import stat
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

import pytest

from suthing import (
    atomic_write,
    batched,
    env_flag,
    expand_path,
    load_env,
    open_compressed,
    setup_logging,
    slugify,
    to_jsonable,
)


def test_batched():
    assert list(batched(range(5), 2)) == [[0, 1], [2, 3], [4]]
    assert list(batched((x for x in "abc"), 3)) == [["a", "b", "c"]]
    assert list(batched([], 3)) == []
    with pytest.raises(ValueError):
        list(batched([1], 0))


@pytest.mark.parametrize(
    "text, kwargs, expected",
    [
        ("  Person / Company ", {}, "Person-Company"),
        ("a.b_c-d", {}, "a.b_c-d"),
        ("///", {"fallback": "schema"}, "schema"),
        ("Café Menü", {"sep": "_", "lower": True, "ascii_fold": True}, "cafe_menu"),
        ("Café", {}, "Caf"),
        ("abc def ghi", {"max_length": 4}, "abc"),
    ],
)
def test_slugify(text, kwargs, expected):
    assert slugify(text, **kwargs) == expected


def test_env_flag(monkeypatch):
    monkeypatch.delenv("SUTHING_FLAG", raising=False)
    assert env_flag("SUTHING_FLAG") is False
    assert env_flag("SUTHING_FLAG", default=True) is True
    for value, expected in [(" Yes ", True), ("1", True), ("off", False), ("", False)]:
        monkeypatch.setenv("SUTHING_FLAG", value)
        assert env_flag("SUTHING_FLAG") is expected
    monkeypatch.setenv("SUTHING_FLAG", "maybe")
    with pytest.raises(ValueError, match="not a boolean"):
        env_flag("SUTHING_FLAG")


def test_load_env(tmp_path, monkeypatch):
    monkeypatch.setenv("SUTHING_KEEP", "old")
    monkeypatch.delenv("SUTHING_NEW", raising=False)
    path = tmp_path / "sample.env"
    path.write_text("SUTHING_KEEP=new\nSUTHING_NEW=1\n")
    assert load_env(path) == {"SUTHING_KEEP": "new", "SUTHING_NEW": "1"}
    assert os.environ["SUTHING_KEEP"] == "old"
    assert os.environ["SUTHING_NEW"] == "1"
    load_env(path, override=True)
    assert os.environ["SUTHING_KEEP"] == "new"
    with pytest.raises(FileNotFoundError):
        load_env(tmp_path / "absent.env")


class Kind(Enum):
    A = "a"


@dataclasses.dataclass
class Point:
    x: int
    when: datetime


def test_to_jsonable():
    when = datetime(2026, 1, 2, tzinfo=UTC)
    value = {
        Kind.A: (Kind.A, Decimal("1.5"), math.nan, math.inf),
        1: {3, 1, 2},
        "id": UUID(int=1),
        "p": pathlib.PurePosixPath("/x"),
        "pt": Point(1, when),
    }
    assert to_jsonable(value) == {
        "a": ["a", 1.5, None, None],
        "1": [1, 2, 3],
        "id": "00000000-0000-0000-0000-000000000001",
        "p": "/x",
        "pt": {"x": 1, "when": "2026-01-02T00:00:00+00:00"},
    }
    assert to_jsonable(math.nan, nan="NaN") == "NaN"
    with pytest.raises(TypeError, match="object"):
        to_jsonable(object())


def test_to_jsonable_numpy():
    np = pytest.importorskip("numpy")
    assert to_jsonable({"a": np.arange(3), "f": np.float32(0.5)}) == {
        "a": [0, 1, 2],
        "f": 0.5,
    }


def test_expand_path(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    assert expand_path("~/x") == tmp_path.resolve() / "x"


def test_atomic_write(tmp_path):
    path = atomic_write(tmp_path / "d" / "x.txt", "é", mkdir=True, durable=True)
    assert path.read_text(encoding="utf-8") == "é"
    mode = stat.S_IMODE(path.stat().st_mode)
    umask = os.umask(0)
    os.umask(umask)
    assert mode == 0o666 & ~umask


def test_open_compressed_rejects_text_mode(tmp_path):
    with (
        pytest.raises(ValueError, match="mode"),
        open_compressed(tmp_path / "x.gz", "w"),
    ):
        pass


@pytest.fixture()
def clean_root_logger():
    root = logging.getLogger()
    saved = root.handlers[:], root.level
    yield root
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    for handler in saved[0]:
        root.addHandler(handler)
    root.setLevel(saved[1])


def test_setup_logging_defaults(clean_root_logger):
    setup_logging("DEBUG", force=True)
    assert clean_root_logger.level == logging.DEBUG


def test_setup_logging_from_yaml(tmp_path, clean_root_logger):
    config = tmp_path / "logging.yaml"
    config.write_text(
        "handlers:\n  h:\n    class: logging.NullHandler\n"
        "root:\n  level: WARNING\n  handlers: [h]\n"
    )
    setup_logging(config=config, force=True)
    assert clean_root_logger.level == logging.WARNING
    assert [type(h).__name__ for h in clean_root_logger.handlers] == ["NullHandler"]


def test_setup_logging_rejects_unknown_config(tmp_path):
    config = tmp_path / "logging.toml"
    config.write_text("")
    with pytest.raises(ValueError, match="unsupported"):
        setup_logging(config=config)

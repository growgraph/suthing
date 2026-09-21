import pathlib

import pytest

DATA = pathlib.Path(__file__).parent / "data"


@pytest.fixture()
def data_dir() -> pathlib.Path:
    return DATA


@pytest.fixture()
def rows() -> list[dict[str, str]]:
    return [{"a": "abc"}, {"b": "abc"}]

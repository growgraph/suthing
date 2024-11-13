import os

import pytest


@pytest.fixture()
def parameters():
    cpath = os.path.dirname(os.path.realpath(__file__))
    ref_json = [{"a": "abc"}, {"b": "abc"}]
    return [cpath, ref_json]

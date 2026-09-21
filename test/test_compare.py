import math

import pytest

from suthing import MISSING, diff, equals


def test_length_mismatch_is_a_difference():
    # 0.5.x compared with zip() and reported these as equal.
    assert not equals([1, 2], [1])
    assert not equals([1], [1, 2])
    assert [str(d) for d in diff({"a": [1, 2]}, {"a": [1]})] == [
        "$.a[1]: missing item (expected=2, actual=<missing>)"
    ]


def test_nested_paths():
    expected = {"users": [{"name": "Ann"}, {"name": "Bob"}], "odd key": 1}
    actual = {"users": [{"name": "Ann"}, {"name": "Rob"}], "extra": 2}
    found = diff(expected, actual)
    assert [(d.path, d.reason) for d in found] == [
        ("$.users[1].name", "values differ"),
        ("$['odd key']", "missing key"),
        ("$.extra", "unexpected key"),
    ]
    assert found[1].actual is MISSING


def test_equal_structures():
    a = {"a": [1, (2, 3)], "b": {"c": None}, "s": {1, 2}}
    b = {"b": {"c": None}, "a": [1, [2, 3]], "s": {2, 1}}
    assert diff(a, b) == []
    assert equals(a, b)


def test_sets_compare_as_sets():
    found = diff({1, 2}, {2, 3})
    assert {(d.reason, d.expected, d.actual) for d in found} == {
        ("missing element", 1, MISSING),
        ("unexpected element", MISSING, 3),
    }


def test_ignore_order():
    assert not equals([1, 2, 2], [2, 1, 2])
    assert equals([1, 2, 2], [2, 1, 2], ignore_order=True)
    assert not equals([1, 2, 2], [2, 1, 1], ignore_order=True)
    assert equals([{"a": 1}, {"b": 2}], [{"b": 2}, {"a": 1}], ignore_order=True)


def test_numbers():
    assert equals(1, 1.0)
    assert equals(math.nan, float("nan"))
    assert not equals(1.0, 1.0 + 1e-9)
    assert equals(1.0, 1.0 + 1e-9, rel_tol=1e-6)
    assert equals({"x": [0.0]}, {"x": [1e-12]}, abs_tol=1e-9)


def test_bool_is_not_a_tolerant_number():
    assert diff(True, 1.0000001, rel_tol=0.1)[0].reason == "type bool != float"


def test_type_mismatch():
    assert diff({"a": 1}, [1])[0].reason == "type dict != list"
    assert diff("1", 1)[0].reason == "type str != int"


def test_strings_are_atomic():
    assert diff("abc", "abd")[0].path == "$"


def test_max_diffs():
    assert len(diff(list(range(10)), list(range(10, 20)), max_diffs=3)) == 3


def test_generators_and_tuples():
    assert equals((x for x in [1, 2]), [1, 2])


def test_incomparable_values():
    class Weird:
        def __eq__(self, other):
            raise ValueError("ambiguous")

    found = diff(Weird(), Weird())
    assert found[0].reason == "cannot compare (ValueError)"


@pytest.mark.parametrize("value", [None, 0, "", [], {}])
def test_self_equal(value):
    assert equals(value, value)

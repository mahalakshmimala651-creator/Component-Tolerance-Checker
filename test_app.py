import pytest
from app import parse_engineering_value


@pytest.mark.parametrize("value, expected", [
    ("100", 100.0),
    ("4.7k", 4700.0),
    ("2.2M", 2200000.0),
    ("100m", 0.1),
    ("100u", 0.0001),
    ("100n", 0.0000001),
    ("100p", 0.0000000001),
    ("-10", -10.0),
    ("1e3", 1000.0),
])
def test_engineering_value_conversion(value, expected):
    assert parse_engineering_value(value) == pytest.approx(expected)


@pytest.mark.parametrize("value", [
    None,
    "",
    "--",
    "-",
    "NA",
    "N/A",
    "abc",
])
def test_invalid_engineering_values(value):
    assert parse_engineering_value(value) is None
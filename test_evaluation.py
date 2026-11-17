from decimal import Decimal
from evaluation import parse_value


# Basic parsing tests

def test_parse_valid_integer():
    assert parse_value(100) == Decimal("100")


def test_parse_valid_decimal():
    assert parse_value("105.50") == Decimal("105.50")


def test_parse_invalid_value():
    assert parse_value("abc") is None


def test_parse_none_value():
    assert parse_value(None) is None


# Boundary tests

def test_tolerance_boundary():
    nominal = Decimal("100")
    tolerance = Decimal("5")

    minimum = nominal * (1 - tolerance / 100)
    maximum = nominal * (1 + tolerance / 100)

    assert minimum == Decimal("95")
    assert maximum == Decimal("105")
    assert minimum <= Decimal("105") <= maximum
    assert minimum <= Decimal("95") <= maximum


# SI unit conversion tests

def test_parse_kilo():
    assert parse_value("4.7k") == Decimal("4700")


def test_parse_mega():
    assert parse_value("0.0047M") == Decimal("4700")


def test_parse_milli():
    assert parse_value("100m") == Decimal("0.100")


def test_parse_micro():
    assert parse_value("100u") == Decimal("0.000100")


def test_parse_nano():
    assert parse_value("100n") == Decimal("0.000000100")


def test_parse_pico():
    assert parse_value("100p") == Decimal("0.000000000100")


def test_parse_negative_value():
    assert parse_value("-10") == Decimal("-10")


def test_parse_invalid_text():
    assert parse_value("--") is None


def test_parse_invalid_characters():
    assert parse_value("1O0n") is None


# PASS/FAIL business rule tests

def check_tolerance(nominal, tolerance, measured):
    minimum = nominal * (1 - tolerance / 100)
    maximum = nominal * (1 + tolerance / 100)

    if minimum <= measured <= maximum:
        return "PASS"
    else:
        return "FAIL"


def test_normal_value_pass():
    assert check_tolerance(100, 5, 100) == "PASS"


def test_lower_boundary_pass():
    assert check_tolerance(100, 5, 95) == "PASS"


def test_upper_boundary_pass():
    assert check_tolerance(100, 5, 105) == "PASS"


def test_below_minimum_fail():
    assert check_tolerance(100, 5, 94) == "FAIL"


def test_above_maximum_fail():
    assert check_tolerance(100, 5, 106) == "FAIL"
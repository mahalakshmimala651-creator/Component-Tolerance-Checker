import csv
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from database import get_db_connection


# Project folder
BASE_DIR = Path(__file__).parent

# Output folder
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# SI unit suffixes
UNIT_MULTIPLIERS = {
    "M": Decimal("1000000"),
    "k": Decimal("1000"),
    "m": Decimal("0.001"),
    "u": Decimal("0.000001"),
    "n": Decimal("0.000000001"),
    "p": Decimal("0.000000000001"),
}


def parse_value(value):
    """
    Convert a measurement such as 4.7k or 100n
    into an exact Decimal number.
    """

    value = str(value)

    pattern = r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)[Mkm unp]?$"
    pattern = pattern.replace(" ", "")

    if not re.fullmatch(pattern, value):
        return None

    suffix = value[-1] if value[-1] in UNIT_MULTIPLIERS else ""

    number = value[:-1] if suffix else value

    try:
        result = Decimal(number)

        if suffix:
            result *= UNIT_MULTIPLIERS[suffix]

        return result

    except InvalidOperation:
        return None


# Quick parser tests
if __name__ == "__main__":
    test_values = ["4.7k", "4700", "0.0047M", "100n", "--", "1O0n"]

    for item in test_values:
        print(item, "=", parse_value(item))
def load_project_data():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM part_specs")
        specs = cursor.fetchall()

        cursor.execute("SELECT * FROM lots ORDER BY lot_id")
        lots = cursor.fetchall()

        cursor.execute("""
            SELECT lot_id, sample_no, measured_value
            FROM measurements
            ORDER BY lot_id, sample_no
        """)
        measurements = cursor.fetchall()

        print("\nDatabase data loaded successfully!")
        print("Part specifications:", len(specs))
        print("Lots:", len(lots))
        print("Measurements:", len(measurements))

        return specs, lots, measurements

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    load_project_data()       
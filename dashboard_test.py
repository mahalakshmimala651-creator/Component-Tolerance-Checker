from database import get_db_connection
from evaluation import parse_value

from decimal import Decimal

connection = get_db_connection()
cursor = connection.cursor(dictionary=True)

try:
    query = """
        SELECT
            m.id,
            m.lot_id,
            m.sample_no,
            m.measured_value,
            l.part_no,
            p.nominal_value,
            p.tolerance_pct,
            p.unit
        FROM measurements m
        JOIN lots l ON m.lot_id = l.lot_id
        JOIN part_specs p ON l.part_no = p.part_no
        ORDER BY m.id
    """

    cursor.execute(query)
    records = cursor.fetchall()

    passed = 0
    failed = 0
    skipped = 0

    for row in records:
        nominal = parse_value(row["nominal_value"])
        measured = parse_value(row["measured_value"])

        if nominal is None or measured is None:
            skipped += 1
            continue

        tolerance = Decimal(str(row["tolerance_pct"]))

        minimum = nominal * (1 - tolerance / 100)
        maximum = nominal * (1 + tolerance / 100)

        if minimum <= measured <= maximum:
            passed += 1
        else:
            failed += 1

    print("\n===== PRODUCTION EVALUATION REPORT =====")
    print("Total measurements:", len(records))
    print("PASS:", passed)
    print("FAIL:", failed)
    print("Skipped:", skipped)

    if passed + failed > 0:
        accuracy = passed / (passed + failed) * 100
        print("PASS percentage:", round(accuracy, 2), "%")

finally:
    cursor.close()
    connection.close()
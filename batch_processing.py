import csv
from pathlib import Path
from database import get_db_connection

# Correct college sample data folder
DATA_DIR = (
    Path(__file__).parent
    / "sample_data"
    / "E018-ECE-050-sample-data"
)


def load_csv(filename, columns, required, sql, converters=None):
    file_path = DATA_DIR / filename
    converters = converters or {}

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    connection = get_db_connection()
    cursor = connection.cursor()

    loaded = 0
    skipped = 0

    try:
        with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                data = {
                    (key or "").strip().lower(): (value or "").strip()
                    for key, value in row.items()
                    if key is not None
                }

                if not all(data.get(field) for field in required):
                    skipped += 1
                    continue

                try:
                    values = tuple(
                        converters[field](data[field])
                        if field in converters else data[field]
                        for field in columns
                    )

                    cursor.execute(sql, values)
                    loaded += 1

                except (ValueError, TypeError):
                    skipped += 1

        connection.commit()
        print(f"{filename}: {loaded} records loaded, {skipped} skipped")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def load_all_data():

    load_csv(
        "part_specs.csv",
        ["part_no", "part_type", "nominal_value", "unit",
         "tolerance_pct", "description"],
        ["part_no", "part_type", "nominal_value", "unit",
         "tolerance_pct"],
        """INSERT INTO part_specs
        (part_no, part_type, nominal_value, unit,
         tolerance_pct, description)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        part_type=VALUES(part_type),
        nominal_value=VALUES(nominal_value),
        unit=VALUES(unit),
        tolerance_pct=VALUES(tolerance_pct),
        description=VALUES(description)"""
    )

    load_csv(
        "suppliers.csv",
        ["supplier_id", "supplier_name", "city"],
        ["supplier_id", "supplier_name", "city"],
        """INSERT INTO suppliers
        (supplier_id, supplier_name, city)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        supplier_name=VALUES(supplier_name),
        city=VALUES(city)"""
    )

    load_csv(
        "lots.csv",
        ["lot_id", "part_no", "supplier_id", "lot_size", "received_date"],
        ["lot_id", "part_no", "supplier_id", "lot_size", "received_date"],
        """INSERT INTO lots
        (lot_id, part_no, supplier_id, lot_size, received_date)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        part_no=VALUES(part_no),
        supplier_id=VALUES(supplier_id),
        lot_size=VALUES(lot_size),
        received_date=VALUES(received_date)""",
        {"lot_size": int}
    )

    load_csv(
        "measurements.csv",
        ["lot_id", "sample_no", "measured_value"],
        ["lot_id", "sample_no", "measured_value"],
        """INSERT INTO measurements
        (lot_id, sample_no, measured_value)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        measured_value=VALUES(measured_value)""",
        {"sample_no": int}
    )


if __name__ == "__main__":
    print("ECE-050 BATCH PROCESSING")
    print("-------------------------")

    try:
        load_all_data()
        print("CSV loading completed!")

    except Exception as error:
        print("Error:", error)
from datetime import datetime
from database import get_db_connection


def generate_report():
    connection = get_db_connection()
    cursor = connection.cursor()

    tables = {
        "Part Specifications": "part_specs",
        "Suppliers": "suppliers",
        "Production Lots": "lots",
        "Measurements": "measurements"
    }

    report = [
        "ECE-050 COMPONENT TOLERANCE CHECKER",
        "BATCH PROCESSING REPORT",
        "=" * 45,
        f"Generated on: {datetime.now()}",
        ""
    ]

    for display_name, table_name in tables.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        report.append(f"{display_name}: {count} records")

    report.append("")
    report.append("Report generated successfully.")

    with open("batch_report.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(report))

    cursor.close()
    connection.close()

    print("Batch report generated successfully!")
    print("Report saved as batch_report.txt")


if __name__ == "__main__":
    generate_report()
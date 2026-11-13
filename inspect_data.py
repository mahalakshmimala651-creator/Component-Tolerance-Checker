from database import get_db_connection

connection = get_db_connection()
cursor = connection.cursor(dictionary=True)

try:
    print("\n--- PART SPECIFICATIONS ---")
    cursor.execute("SELECT * FROM part_specs LIMIT 5")
    for row in cursor.fetchall():
        print(row)

    print("\n--- PRODUCTION LOTS ---")
    cursor.execute("SELECT * FROM lots LIMIT 5")
    for row in cursor.fetchall():
        print(row)

    print("\n--- MEASUREMENTS ---")
    cursor.execute("SELECT * FROM measurements LIMIT 5")
    for row in cursor.fetchall():
        print(row)

finally:
    cursor.close()
    connection.close()
from database import get_db_connection

connection = get_db_connection()
cursor = connection.cursor()

tables = ["part_specs", "lots", "measurements"]

for table in tables:
    print("\nTable:", table)
    cursor.execute(f"DESCRIBE {table}")

    for column in cursor.fetchall():
        print(column[0], "-", column[1])

cursor.close()
connection.close()

print("\nDatabase structure checked successfully!")
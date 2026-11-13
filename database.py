import os
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ.get("MYSQL_PASSWORD"),
        database="ece050_db",
        port=3307
    )


def save_inspection(component, rated, tolerance,
                    measured, minimum, maximum, result):

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO component_inspections
    (component_name, rated_value, tolerance_percent,
     measured_value, minimum_value, maximum_value,
     inspection_result)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        component, rated, tolerance,
        measured, minimum, maximum, result
    )

    try:
        cursor.execute(query, values)
        connection.commit()
        print("Inspection saved successfully!")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    try:
        connection = get_db_connection()
        print("MySQL Database Connected Successfully!")
        connection.close()

    except mysql.connector.Error as error:
        print("Database Error:", error)
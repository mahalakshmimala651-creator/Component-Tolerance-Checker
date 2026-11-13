from database import get_db_connection

print("ECE-050 Project")
print("Python setup successful")
print("Project is ready to start")

try:
    connection = get_db_connection()

    if connection.is_connected():
        print("Database connected successfully!")

    connection.close()

except Exception as error:
    print("Database connection failed!")
    print(error)
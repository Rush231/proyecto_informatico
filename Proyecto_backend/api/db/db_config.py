import mysql.connector
import os 

def get_db_connection():
    connection = mysql.connector.connect(
        host = os.getenv('DB_HOST', 'localhost'),
        port = os.getenv('DB_PORT', 3306),
        user = os.getenv('DB_USER', 'FlaskUser'),
        password = os.getenv("DB_PASSWORD", 'password123'),
        database = os.getenv('DB_NAME', 'Sistema_Turnos')

    )

    return connection
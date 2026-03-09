import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "lost2found")
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, password, role FROM users WHERE role = 'admin'")
    users = cursor.fetchall()
    for u in users:
        print(f"Repr: {repr(u)}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")

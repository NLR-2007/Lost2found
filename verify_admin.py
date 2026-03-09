import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

load_dotenv()
conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'lost2found')
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT id, email, password, role FROM users WHERE role = 'admin'")
users = cursor.fetchall()
for u in users:
    pwd_check = check_password_hash(u['password'], 'boss@123')
    print("Email:", repr(u['email']))
    print("Role:", u['role'])
    print("Password valid:", pwd_check)
conn.close()

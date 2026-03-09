"""
add_admin2.py
-------------
One-time script to insert Admin2@l2f.com into the live database.
Run once:  venv\Scripts\python add_admin2.py
"""
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

ADMIN2_EMAIL = "Admin2@l2f.com"
ADMIN2_PASSWORD = "krsna@1234"
ADMIN2_NAME = "Admin2"

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'lost2found')
)
cursor = conn.cursor(dictionary=True)

# Check if Admin2 already exists
cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(%s)", (ADMIN2_EMAIL,))
existing = cursor.fetchone()

if existing:
    print(f"Admin2 ({ADMIN2_EMAIL}) already exists in DB (id={existing['id']}). Updating password...")
    new_hash = generate_password_hash(ADMIN2_PASSWORD)
    cursor.execute(
        "UPDATE users SET password = %s, role = 'admin', name = %s WHERE LOWER(email) = LOWER(%s)",
        (new_hash, ADMIN2_NAME, ADMIN2_EMAIL)
    )
    print("Password updated.")
else:
    print(f"Inserting new admin: {ADMIN2_EMAIL}")
    new_hash = generate_password_hash(ADMIN2_PASSWORD)
    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
        (ADMIN2_NAME, ADMIN2_EMAIL, new_hash, "admin")
    )
    print("Admin2 inserted successfully.")

conn.commit()

# Verify
cursor.execute("SELECT id, name, email, role FROM users WHERE LOWER(email) = LOWER(%s)", (ADMIN2_EMAIL,))
row = cursor.fetchone()
print(f"\n--- Verification ---")
print(f"ID    : {row['id']}")
print(f"Name  : {row['name']}")
print(f"Email : {row['email']}")
print(f"Role  : {row['role']}")

# Verify password hash
cursor2 = conn.cursor(dictionary=True)
cursor2.execute("SELECT password FROM users WHERE LOWER(email) = LOWER(%s)", (ADMIN2_EMAIL,))
pw_row = cursor2.fetchone()
ok = check_password_hash(pw_row['password'], ADMIN2_PASSWORD)
print(f"Password check: {'PASS ✓' if ok else 'FAIL ✗'}")

cursor.close()
cursor2.close()
conn.close()
print("\nDone! Admin2@l2f.com is ready to log in.")

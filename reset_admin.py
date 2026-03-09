import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

ADMIN_EMAIL = "admin@l2f.com"
ADMIN_PASSWORD = "boss@123"

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'lost2found')
)
cursor = conn.cursor()

# Generate a fresh hash
new_hash = generate_password_hash(ADMIN_PASSWORD)
print("Generated hash:", new_hash)

# Verify the hash immediately
verified = check_password_hash(new_hash, ADMIN_PASSWORD)
print("Hash self-check:", verified)

# Delete all admins
cursor.execute("DELETE FROM users WHERE role = 'admin'")
print("Deleted existing admin rows:", cursor.rowcount)

# Insert fresh admin
cursor.execute(
    "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
    ("System Admin", ADMIN_EMAIL, new_hash, "admin")
)
print("Inserted new admin row:", cursor.rowcount)
conn.commit()

# Read back
cursor2 = conn.cursor(dictionary=True)
cursor2.execute("SELECT id, email, password, role FROM users WHERE role = 'admin'")
row = cursor2.fetchone()
print("DB email:", repr(row['email']))
print("DB password (first 30 chars):", row['password'][:30])
verify_db = check_password_hash(row['password'], ADMIN_PASSWORD)
print("DB password check:", verify_db)

conn.close()

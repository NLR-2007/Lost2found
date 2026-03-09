import mysql.connector, os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

load_dotenv()
conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'lost2found')
)
cur = conn.cursor(dictionary=True)
cur.execute("SELECT id, name, email, role, password FROM users WHERE role='admin'")
rows = cur.fetchall()
print("Found %d admin(s):" % len(rows))
for r in rows:
    pw_boss  = check_password_hash(r['password'], 'boss@123')
    pw_krsna = check_password_hash(r['password'], 'krsna@1234')
    print("  [%s] %s | %s | role=%s" % (r['id'], r['name'], r['email'], r['role']))
    print("       boss@123=%s | krsna@1234=%s" % (pw_boss, pw_krsna))
conn.close()
print("Verification complete.")

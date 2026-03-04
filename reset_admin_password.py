import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("db.sqlite")
cur = conn.cursor()

new_password = generate_password_hash("admin123")

cur.execute(
    "UPDATE users SET password=? WHERE email=?",
    (new_password, "admin@gmail.com")
)

conn.commit()
conn.close()

print("✅ Admin password reset to admin123")

import sqlite3

conn = sqlite3.connect('db.sqlite')
cur = conn.cursor()

# USERS TABLE
cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'user'
)
            UPDATE users SET role='admin' WHERE email='sarthak9090@gmail.com';
""")



# EVENTS TABLE
cur.execute("""
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    date TEXT,
    venue TEXT,
    price INTEGER
)
""")

# BOOKINGS TABLE
cur.execute("""
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_id INTEGER,
    payment_status TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(event_id) REFERENCES events(id)
)
""")



conn.commit()
conn.close()

print("Database created successfully")

import sqlite3

conn = sqlite3.connect("db.sqlite")
cur = conn.cursor()

cur.execute("""
INSERT INTO events (title, description, date, venue, price)
VALUES
('Tech Conference 2026', 'Technology conference', '2026-02-10', 'New Delhi', 500),
('Music Fest', 'Live music concert', '2026-03-15', 'Mumbai', 800),
('Startup Meetup', 'Startup networking event', '2026-01-25', 'Bangalore', 300)
""")

conn.commit()
conn.close()

print("✅ Events added successfully")

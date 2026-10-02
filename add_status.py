import sqlite3
import os

# Use the exact database location
db_path = os.path.join(
    os.path.dirname(__file__),
    "instance",
    "chess_academy.db"
)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    ALTER TABLE registration
    ADD COLUMN status TEXT NOT NULL DEFAULT 'Pending'
""")

conn.commit()
conn.close()

print("Status column added successfully!")
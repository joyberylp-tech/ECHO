import sqlite3

connection = sqlite3.connect("echo.db")

users = connection.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
).fetchone()

columns = [
    row[1] for row in connection.execute("PRAGMA table_info(notes)")
]

total_notes = connection.execute(
    "SELECT COUNT(*) FROM notes"
).fetchone()[0]

print("Users table:", users)
print("Notes columns:", columns)
print("Total notes:", total_notes)

connection.close()
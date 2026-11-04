import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "echo.db"


def migrate_database():
    connection = sqlite3.connect(DATABASE)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)

        columns = [
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(notes)"
            ).fetchall()
        ]

        if "user_id" not in columns:
            connection.execute("""
                ALTER TABLE notes
                ADD COLUMN user_id INTEGER REFERENCES users(id)
            """)

        connection.commit()

        print("Database migration completed.")
        print("Users table created or verified.")
        print("Existing notes preserved.")

        total = connection.execute(
            "SELECT COUNT(*) FROM notes"
        ).fetchone()[0]

        print("Total existing notes:", total)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    migrate_database()
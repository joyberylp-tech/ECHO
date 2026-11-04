
import unittest
import sqlite3
import tempfile

from pathlib import Path
from unittest.mock import patch

import flask_app


class ECHOFlaskTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_database = Path(self.temp_dir.name) / "test_echo.db"

        self.database_patch = patch.object(
            flask_app, "DATABASE", self.test_database
        )
        self.database_patch.start()

        connection = sqlite3.connect(self.test_database)

        connection.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                user_id INTEGER REFERENCES users(id)
            )
        """)

        connection.execute("""
            INSERT INTO notes (title, content)
            VALUES ('Old Note', 'Existing note content')
        """)

        connection.commit()
        connection.close()

        flask_app.app.config["TESTING"] = True
        flask_app.app.config["WTF_CSRF_ENABLED"] = False

        self.client = flask_app.app.test_client()

    def tearDown(self):
        self.database_patch.stop()
        self.temp_dir.cleanup()

    def register(self, username, email, password):
        return self.client.post(
            "/register",
            data={
                "username": username,
                "email": email,
                "password": password
            },
            follow_redirects=True
        )

    def login(self, email, password):
        return self.client.post(
            "/login",
            data={
                "email": email,
                "password": password
            },
            follow_redirects=True
        )

    # TEST 1: Registration
    def test_registration(self):
        response = self.register(
            "beryl", "beryl@example.com", "password123"
        )

        self.assertEqual(response.status_code, 200)

    # TEST 2: Password hashing
    def test_password_is_hashed(self):
        self.register(
            "beryl", "beryl@example.com", "password123"
        )

        connection = sqlite3.connect(self.test_database)

        password_hash = connection.execute(
            "SELECT password_hash FROM users"
        ).fetchone()[0]

        connection.close()

        self.assertNotEqual(password_hash, "password123")

    # TEST 3: Duplicate email rejection
    def test_duplicate_email_is_rejected(self):
        self.register(
            "beryl", "beryl@example.com", "password123"
        )

        self.register(
            "another", "beryl@example.com", "password456"
        )

        connection = sqlite3.connect(self.test_database)

        count = connection.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        connection.close()

        self.assertEqual(count, 1)

    # TEST 4: First user receives existing notes
    def test_first_user_receives_existing_notes(self):
        self.register(
            "beryl", "beryl@example.com", "password123"
        )

        connection = sqlite3.connect(self.test_database)

        user_id = connection.execute(
            "SELECT id FROM users"
        ).fetchone()[0]

        note_owner = connection.execute(
            "SELECT user_id FROM notes"
        ).fetchone()[0]

        connection.close()

        self.assertEqual(note_owner, user_id)

    # TEST 5: Login with correct password
    def test_login_with_correct_password(self):
        self.register(
            "beryl", "beryl@example.com", "password123"
        )

        response = self.login(
            "beryl@example.com", "password123"
        )

        self.assertIn(b"Old Note", response.data)

    # TEST 6: Login with incorrect password
    def test_login_with_wrong_password(self):
        self.register(
            "beryl", "beryl@example.com", "password123"
        )

        response = self.login(
            "beryl@example.com", "wrongpassword"
        )

        self.assertNotIn(b"Old Note", response.data)

    # TEST 7: Second user cannot see first user's notes
    def test_second_user_cannot_see_first_users_notes(self):
        self.register(
            "beryl", "beryl@example.com", "password123"
        )

        self.client.post("/logout")

        self.register(
            "second", "second@example.com", "password456"
        )

        response = self.login(
            "second@example.com", "password456"
        )

        self.assertNotIn(b"Old Note", response.data)

    # TEST 8: Logged-out users cannot access home
    def test_logged_out_user_cannot_access_home(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 302)

        self.assertIn("/login", response.location)

    # TEST 9: Second user cannot edit or delete first user's note
    def test_second_user_cannot_edit_or_delete_first_users_note(self):
        self.register(
            "beryl", "beryl@example.com", "password123"
        )

        self.client.post("/logout")

        self.register(
            "second", "second@example.com", "password456"
        )

        self.login("second@example.com", "password456")

        edit_response = self.client.get("/edit/1")

        self.assertEqual(edit_response.status_code, 302)

        self.client.post("/delete/1")

        connection = sqlite3.connect(self.test_database)

        note = connection.execute(
            "SELECT title FROM notes WHERE id = 1"
        ).fetchone()

        connection.close()

        self.assertIsNotNone(note)


if __name__ == "__main__":
    unittest.main()
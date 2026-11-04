import os
import sqlite3
from pathlib import Path
from functools import wraps

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, session
)

from flask_wtf.csrf import CSRFProtect
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

app = Flask(__name__)

app.secret_key = os.environ.get(
    "ECHO_SECRET_KEY",
    "echo-local-development-key-change-before-deployment"
)

csrf = CSRFProtect(app)

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "echo.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Please complete all fields.", "error")
            return redirect(url_for("register"))

        if len(username) > 50 or len(email) > 254:
            flash("Username or email is too long.", "error")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return redirect(url_for("register"))

        connection = get_connection()

        try:
            with connection:
                existing_users = connection.execute(
                    "SELECT COUNT(*) FROM users"
                ).fetchone()[0]

                password_hash = generate_password_hash(password)

                cursor = connection.execute(
                    """
                    INSERT INTO users (username, email, password_hash)
                    VALUES (?, ?, ?)
                    """,
                    (username, email, password_hash)
                )

                new_user_id = cursor.lastrowid

                # Only the first registered user receives old notes.
                if existing_users == 0:
                    connection.execute(
                        """
                        UPDATE notes
                        SET user_id = ?
                        WHERE user_id IS NULL
                        """,
                        (new_user_id,)
                    )

            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("That username or email is already registered.", "error")

        finally:
            connection.close()

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = get_connection()

        try:
            user = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()

        finally:
            connection.close()

        if user and check_password_hash(
            user["password_hash"], password
        ):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            flash("Welcome to ECHO!", "success")
            return redirect(url_for("home"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


# LOGOUT
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have logged out successfully.", "success")
    return redirect(url_for("login"))


# HOME PAGE
@app.route("/")
@login_required
def home():

    connection = get_connection()

    try:
        notes = connection.execute(
            """
            SELECT * FROM notes
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (session["user_id"],)
        ).fetchall()

        return render_template("index.html", notes=notes)

    finally:
        connection.close()


# SEARCH NOTES
@app.route("/search")
@login_required
def search_notes():

    keyword = request.args.get("keyword", "").strip()

    connection = get_connection()

    try:
        if keyword:
            notes = connection.execute(
                """
                SELECT * FROM notes
                WHERE user_id = ?
                AND (title LIKE ? OR content LIKE ?)
                ORDER BY id DESC
                """,
                (
                    session["user_id"],
                    f"%{keyword}%",
                    f"%{keyword}%"
                )
            ).fetchall()

        else:
            notes = connection.execute(
                """
                SELECT * FROM notes
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (session["user_id"],)
            ).fetchall()

        return render_template(
            "index.html",
            notes=notes,
            search_keyword=keyword
        )

    finally:
        connection.close()


# CREATE NOTE
@app.route("/add-note", methods=["POST"])
@login_required
def add_note():

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not title or not content or len(title) > 100 or len(content) > 5000:
        flash("Please enter a valid title and content.", "error")
        return redirect(url_for("home"))

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO notes (title, content, user_id)
            VALUES (?, ?, ?)
            """,
            (title, content, session["user_id"])
        )

        connection.commit()
        flash("Your note was saved successfully!", "success")

    finally:
        connection.close()

    return redirect(url_for("home"))


# EDIT NOTE
@app.route("/edit/<int:note_id>", methods=["GET", "POST"])
@login_required
def edit_note(note_id):

    connection = get_connection()

    try:
        if request.method == "POST":

            title = request.form.get("title", "").strip()
            content = request.form.get("content", "").strip()

            if not title or not content or len(title) > 100 or len(content) > 5000:
                flash("Please enter a valid title and content.", "error")
                return redirect(url_for("edit_note", note_id=note_id))

            cursor = connection.execute(
                """
                UPDATE notes
                SET title = ?, content = ?
                WHERE id = ? AND user_id = ?
                """,
                (title, content, note_id, session["user_id"])
            )

            connection.commit()

            if cursor.rowcount:
                flash("Note updated successfully!", "success")
            else:
                flash("Note not found.", "error")

            return redirect(url_for("home"))

        note = connection.execute(
            """
            SELECT * FROM notes
            WHERE id = ? AND user_id = ?
            """,
            (note_id, session["user_id"])
        ).fetchone()

        if note is None:
            flash("Note not found.", "error")
            return redirect(url_for("home"))

        return render_template("edit.html", note=note)

    finally:
        connection.close()


# DELETE NOTE
@app.route("/delete/<int:note_id>", methods=["POST"])
@login_required
def delete_note(note_id):

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM notes
            WHERE id = ? AND user_id = ?
            """,
            (note_id, session["user_id"])
        )

        connection.commit()

        if cursor.rowcount:
            flash("Note deleted successfully!", "success")
        else:
            flash("Note not found.", "error")

    finally:
        connection.close()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
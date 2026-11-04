import sqlite3


# ---------- DATABASE SETUP ----------

def initialize_database(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    connection.commit()


# ---------- CORE APPLICATION LOGIC ----------

def create_note(connection, title, content):
    title = title.strip()
    content = content.strip()

    if not title or not content:
        return False

    if len(title) > 100:
        return False

    if len(content) > 5000:
        return False

    connection.execute(
        "INSERT INTO notes (title, content) VALUES (?, ?)",
        (title, content)
    )
    connection.commit()
    return True


    connection.execute(
        "INSERT INTO notes (title, content) VALUES (?, ?)",
        (title, content)
    )
    connection.commit()
    return True


def find_notes(connection, keyword):
    keyword = keyword.strip()

    if not keyword:
        return []

    return connection.execute(
        """
        SELECT id, title, content
        FROM notes
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY id DESC
        """,
        (f"%{keyword}%", f"%{keyword}%")
    ).fetchall()


def get_all_notes(connection):
    return connection.execute(
        """
        SELECT id, title, content
        FROM notes
        ORDER BY id DESC
        """
    ).fetchall()


def update_note(connection, note_id, title, content):
    title = title.strip()
    content = content.strip()

    if not title or not content:
        return False

    if len(title) > 100 or len(content) > 5000:
        return False

    cursor = connection.execute(
        """
        UPDATE notes
        SET title = ?, content = ?
        WHERE id = ?
        """,
        (title, content, note_id)
    )

    connection.commit()
    return cursor.rowcount > 0




def remove_note(connection, note_id):
    cursor = connection.execute(
        "DELETE FROM notes WHERE id = ?",
        (note_id,)
    )

    connection.commit()
    return cursor.rowcount > 0


# ---------- USER INTERFACE ----------

def save_note(connection):
    print("\n--- SAVE A NOTE ---")

    title = input("Enter note title: ")
    content = input("Enter note content: ")

    if create_note(connection, title, content):
        print("Note saved successfully!")
    else:
        print("Error: Title and content cannot be empty.")


def search_notes(connection):
    print("\n--- SEARCH NOTES ---")

    keyword = input("Enter a keyword to search: ")
    results = find_notes(connection, keyword)

    if not keyword.strip():
        print("Please enter a search keyword.")
        return

    if not results:
        print("No matching notes found.")
        return

    for note_id, title, content in results:
        print(f"\nID: {note_id}")
        print(f"Title: {title}")
        print(f"Content: {content}")


def view_notes(connection):
    print("\n--- ALL SAVED NOTES ---")

    results = get_all_notes(connection)

    if not results:
        print("No notes saved yet.")
        return

    for note_id, title, content in results:
        print(f"\nID: {note_id}")
        print(f"Title: {title}")
        print(f"Content: {content}")


def edit_note(connection):
    print("\n--- EDIT A NOTE ---")

    try:
        note_id = int(input("Enter the note ID to edit: "))

        existing_note = connection.execute(
            "SELECT id FROM notes WHERE id = ?",
            (note_id,)
        ).fetchone()

        if existing_note is None:
            print("No note found with that ID.")
            return

        title = input("Enter the new title: ")
        content = input("Enter the new content: ")

        if update_note(connection, note_id, title, content):
            print("Note updated successfully!")
        else:
            print("Error: Title and content cannot be empty.")

    except ValueError:
        print("Invalid ID. Please enter a number.")


def delete_note(connection):
    print("\n--- DELETE A NOTE ---")

    try:
        note_id = int(input("Enter the note ID to delete: "))

        existing_note = connection.execute(
            "SELECT title FROM notes WHERE id = ?",
            (note_id,)
        ).fetchone()

        if existing_note is None:
            print("No note found with that ID.")
            return

        print("Note title:", existing_note[0])

        confirmation = input(
            "Are you sure you want to delete this note? (yes/no): "
        ).strip().lower()

        if confirmation != "yes":
            print("Deletion cancelled.")
            return

        if remove_note(connection, note_id):
            print("Note deleted successfully!")

    except ValueError:
        print("Invalid ID. Please enter a number.")


# ---------- MAIN PROGRAM ----------

def main():
    connection = sqlite3.connect("echo.db")

    try:
        initialize_database(connection)

        while True:
            print("\n================================")
            print("       ECHO KNOWLEDGE SYSTEM")
            print("================================")
            print("1. Save a note")
            print("2. Search notes")
            print("3. View all notes")
            print("4. Edit a note")
            print("5. Delete a note")
            print("6. Exit")
            print("================================")

            choice = input("Choose an option (1-6): ").strip()

            if choice == "1":
                save_note(connection)
            elif choice == "2":
                search_notes(connection)
            elif choice == "3":
                view_notes(connection)
            elif choice == "4":
                edit_note(connection)
            elif choice == "5":
                delete_note(connection)
            elif choice == "6":
                print("Thank you for using ECHO!")
                break
            else:
                print("Invalid choice. Please select 1-6.")

    finally:
        connection.close()
        print("ECHO database connection closed.")


if __name__ == "__main__":
    main()

import sqlite3
import unittest

from echo import (
    initialize_database,
    create_note,
    find_notes,
    get_all_notes,
    update_note,
    remove_note
)


class TestEchoApplication(unittest.TestCase):

    def setUp(self):
        # Create a separate temporary database for every test
        self.connection = sqlite3.connect(":memory:")
        initialize_database(self.connection)

    def tearDown(self):
        # Close the temporary database
        self.connection.close()

    def test_create_note(self):
        result = create_note(
            self.connection,
            "Python",
            "Python is a programming language"
        )

        self.assertTrue(result)

        notes = get_all_notes(self.connection)

        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0][1], "Python")

    def test_reject_empty_note(self):
        result = create_note(
            self.connection,
            "",
            "This note has no title"
        )

        self.assertFalse(result)
        self.assertEqual(len(get_all_notes(self.connection)), 0)


    def test_reject_long_title(self):
        long_title = "A" * 101

        result = create_note(
            self.connection,
            long_title,
            "This title is too long"
        )

        self.assertFalse(result)
        self.assertEqual(len(get_all_notes(self.connection)), 0)


    def test_search_note(self):
        create_note(
            self.connection,
            "Cybersecurity",
            "Protecting computer systems"
        )

        results = find_notes(self.connection, "Cybersecurity")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "Cybersecurity")

    def test_update_note(self):
        create_note(
            self.connection,
            "Old Title",
            "Old Content"
        )

        result = update_note(
            self.connection,
            1,
            "New Title",
            "New Content"
        )

        self.assertTrue(result)

        notes = get_all_notes(self.connection)

        self.assertEqual(notes[0][1], "New Title")
        self.assertEqual(notes[0][2], "New Content")

    def test_delete_note(self):
        create_note(
            self.connection,
            "Temporary Note",
            "This note will be deleted"
        )

        result = remove_note(self.connection, 1)

        self.assertTrue(result)
        self.assertEqual(len(get_all_notes(self.connection)), 0)

    def test_update_missing_note(self):
        result = update_note(
            self.connection,
            99999,
            "New Title",
            "New Content"
        )

        self.assertFalse(result)

    def test_delete_missing_note(self):
        result = remove_note(self.connection, 99999)

        self.assertFalse(result)


    def test_search_treats_input_as_data(self):
        create_note(
            self.connection,
            "Python",
            "Learning database security"
        )

        suspicious_input = "' OR '1'='1"

        results = find_notes(self.connection, suspicious_input)

        self.assertEqual(results, [])


    def test_reject_long_content_when_updating(self):
        create_note(
            self.connection,
            "Python",
            "A short note"
        )

        long_content = "A" * 5001

        result = update_note(
            self.connection,
            1,
            "Python",
            long_content
        )

        self.assertFalse(result)

        notes = get_all_notes(self.connection)

        self.assertEqual(notes[0][2], "A short note")

    def test_reject_long_title_when_updating(self):
        create_note(
            self.connection,
            "Python",
            "A short note"
        )

        long_title = "A" * 101

        result = update_note(
            self.connection,
            1,
            long_title,
            "Updated content"
        )

        self.assertFalse(result)

        notes = get_all_notes(self.connection)

        self.assertEqual(notes[0][1], "Python")

    def test_reject_empty_content(self):
        result = create_note(
            self.connection,
            "Python",
            ""
        )

        self.assertFalse(result)
        self.assertEqual(len(get_all_notes(self.connection)), 0) 

    def test_reject_empty_content_when_updating(self):
        create_note(
            self.connection,
            "Python",
            "Original content"
        )

        result = update_note(
            self.connection,
            1,
            "Python",
            ""
        )

        self.assertFalse(result)

        notes = get_all_notes(self.connection)

        self.assertEqual(notes[0][2], "Original content")
   
    def test_reject_long_content(self):
        long_content = "A" * 5001

        result = create_note(
            self.connection,
            "Python",
            long_content
        )

        self.assertFalse(result)
        self.assertEqual(len(get_all_notes(self.connection)), 0)

    def test_reject_title_with_only_spaces(self):
        result = create_note(
            self.connection,
            "     ",
            "This note has an invalid title"
        )

        self.assertFalse(result)
        self.assertEqual(len(get_all_notes(self.connection)), 0)

    def test_reject_title_with_only_spaces_when_updating(self):
        create_note(
            self.connection,
            "Python",
            "Original content"
        )

        result = update_note(
            self.connection,
            1,
            "     ",
            "Updated content"
        )

        self.assertFalse(result)

        notes = get_all_notes(self.connection)

        self.assertEqual(notes[0][1], "Python")

    def test_reject_content_with_only_spaces(self):
        result = create_note(
            self.connection,
            "Python",
            "     "
        )

        self.assertFalse(result)
        self.assertEqual(len(get_all_notes(self.connection)), 0)

    def test_reject_content_with_only_spaces_when_updating(self):
        create_note(
            self.connection,
            "Python",
            "Original content"
        )

        result = update_note(
            self.connection,
            1,
            "Python",
            "     "
        )

        self.assertFalse(result)

        notes = get_all_notes(self.connection)

        self.assertEqual(notes[0][2], "Original content")

    def test_search_is_case_insensitive(self):
        create_note(
            self.connection,
            "Python Programming",
            "Learning databases"
        )

        results = find_notes(self.connection, "python")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "Python Programming")
    def test_search_inside_note_content(self):
        create_note(
            self.connection,
            "My Study Notes",
            "Learning Python programming"
        )

        results = find_notes(self.connection, "programming")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "My Study Notes")
    def test_search_with_extra_spaces(self):
        create_note(
            self.connection,
            "Python Programming",
            "Learning databases"
        )

        results = find_notes(self.connection, "   Python   ")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "Python Programming")
    def test_search_with_no_matching_keyword(self):
        create_note(
            self.connection,
            "Python Programming",
            "Learning databases"
        )

        results = find_notes(self.connection, "Java")

        self.assertEqual(len(results), 0)
    def test_search_with_empty_keyword(self):
        create_note(
            self.connection,
            "Python Programming",
            "Learning databases"
        )

        results = find_notes(self.connection, "")

        self.assertEqual(len(results), 0)
    def test_search_partial_word(self):
        create_note(
            self.connection,
            "Python Programming",
            "Learning databases"
        )

        results = find_notes(self.connection, "gram")

        self.assertEqual
           
    def test_search_returns_multiple_matching_notes(self):
        create_note(
            self.connection,
            "Python Basics",
            "Variables and data types"
        )

        create_note(
            self.connection,
            "Advanced Python",
            "Functions and classes"
        )

        results = find_notes(self.connection, "Python")

        self.assertEqual(len(results), 2)

    def test_search_results_newest_first(self):
        create_note(self.connection, "Python First", "First note")
        create_note(self.connection, "Python Second", "Second note")

        results = find_notes(self.connection, "Python")

        self.assertEqual(results[0][1], "Python Second")
        self.assertEqual(results[1][1], "Python First")

    def test_search_title_only(self):
        create_note(
            self.connection,
            "Database Security",
            "Learning computer fundamentals"
        )

        results = find_notes(self.connection, "Security")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "Database Security")

    def test_search_with_only_spaces(self):
        create_note(
            self.connection,
            "Python",
            "Learning programming"
        )

        results = find_notes(self.connection, "     ")

        self.assertEqual(len(results), 0)

    def test_create_note_removes_extra_spaces(self):
        result = create_note(
            self.connection,
            "   Python   ",
            "   Learning databases   "
        )

        notes = get_all_notes(self.connection)

        self.assertTrue(result)
        self.assertEqual(notes[0][1], "Python")
        self.assertEqual(notes[0][2], "Learning databases")

    def test_update_note_removes_extra_spaces(self):
        create_note(
            self.connection,
            "Python",
            "Original content"
        )

        result = update_note(
            self.connection,
            1,
            "   Java   ",
            "   Updated content   "
        )

        notes = get_all_notes(self.connection)

        self.assertTrue(result)
        self.assertEqual(notes[0][1], "Java")
        self.assertEqual(notes[0][2], "Updated content")

    def test_accept_maximum_title_length(self):
        title = "A" * 100

        result = create_note(
            self.connection,
            title,
            "Valid content"
        )

        self.assertTrue(result)
        self.assertEqual(len(get_all_notes(self.connection)), 1)

    def test_accept_maximum_content_length(self):
        content = "A" * 5000

        result = create_note(
            self.connection,
            "Python",
            content
        )

        self.assertTrue(result)
        notes = get_all_notes(self.connection)

        self.assertEqual(len(notes[0][2]), 5000)

    def test_update_accepts_maximum_lengths(self):
        create_note(
            self.connection,
            "Python",
            "Original content"
        )

        title = "B" * 100
        content = "C" * 5000

        result = update_note(
            self.connection,
            1,
            title,
            content
        )

        notes = get_all_notes(self.connection)

        self.assertTrue(result)
        self.assertEqual(len(notes[0][1]), 100)
        self.assertEqual(len(notes[0][2]), 5000)

    def test_delete_only_selected_note(self):
        create_note(
            self.connection,
            "Python",
            "Python content"
        )

        create_note(
            self.connection,
            "Java",
            "Java content"
        )

        result = remove_note(self.connection, 1)

        notes = get_all_notes(self.connection)

        self.assertTrue(result)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0][1], "Java")

    def test_all_notes_newest_first(self):
        create_note(self.connection, "First Note", "First content")
        create_note(self.connection, "Second Note", "Second content")
        create_note(self.connection, "Third Note", "Third content")

        notes = get_all_notes(self.connection)

        self.assertEqual(notes[0][1], "Third Note")
        self.assertEqual(notes[1][1], "Second Note")
        self.assertEqual(notes[2][1], "First Note")
            

if __name__ == "__main__":
    unittest.main()


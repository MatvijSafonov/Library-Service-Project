from django.db import IntegrityError
from django.test import TestCase

from library.models import Author, Book


class AuthorModelTests(TestCase):
    """
    Test suite for the Author model.
    """
    def setUp(self):
        """
        Set up data for the Author model tests.
        """
        self.author_data = {
            "first_name": "Test",
            "last_name": "Author",
            "pseudonym": "TA",
        }

    def test_create_author(self):
        """
        Test that an Author instance can be successfully created with valid data.
        """
        author = Author.objects.create(**self.author_data)

        self.assertEqual(author.first_name, self.author_data["first_name"])
        self.assertEqual(author.last_name, self.author_data["last_name"])
        self.assertEqual(author.pseudonym, self.author_data["pseudonym"])

    def test_author_str_method(self):
        """
        Test that the string representation of an Author instance is correct.
        """
        author = Author.objects.create(**self.author_data)
        expected_str = (
            f"{self.author_data['first_name']} {self.author_data['last_name']}"
        )
        self.assertEqual(str(author), expected_str)

    def test_author_full_name_method(self):
        """
        Test that the `full_name` method of the Author model returns the correct value.
        """
        author = Author.objects.create(**self.author_data)
        expected_full_name = (
            f"{self.author_data['first_name']} {self.author_data['last_name']}"
        )
        self.assertEqual(author.full_name(), expected_full_name)

    def test_unique_author_constraint(self):
        """
        Test that an IntegrityError is raised when trying to create duplicate Author instances.
        """
        Author.objects.create(**self.author_data)
        with self.assertRaises(IntegrityError):
            Author.objects.create(**self.author_data)


class BookModelTests(TestCase):
    """
    Test suite for the Book model.
    """
    def setUp(self):
        """
        Set up data for the Book model tests.
        """
        self.author = Author.objects.create(first_name="Test", last_name="Author")
        self.book_data = {
            "title": "Test Book",
            "author": self.author,
            "cover": "soft",
            "inventory": 5,
            "daily_fee": "10.50",
        }

    def test_create_book(self):
        """
        Test that a Book instance can be successfully created with valid data.
        """
        book = Book.objects.create(**self.book_data)

        self.assertEqual(book.title, self.book_data["title"])
        self.assertEqual(book.author, self.author)
        self.assertEqual(book.cover, self.book_data["cover"])
        self.assertEqual(book.inventory, self.book_data["inventory"])
        self.assertEqual(str(book.daily_fee), self.book_data["daily_fee"])

    def test_book_str_method(self):
        """
        Test that the string representation of a Book instance is correct.
        """
        book = Book.objects.create(**self.book_data)
        expected_str = f"{self.book_data['title']} by {self.author} ({self.book_data['daily_fee']})"
        self.assertEqual(str(book), expected_str)

    def test_book_cover_choices(self):
        """
        Test that the `cover` field of the Book model accepts only valid choices.
        """
        book = Book.objects.create(**self.book_data)
        valid_choices = dict(Book.COVER_CHOICES).keys()
        self.assertIn(book.cover, valid_choices)

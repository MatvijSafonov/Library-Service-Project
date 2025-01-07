from django.test import TestCase

from library.models import Author, Book
from library.serializers import (
    AuthorSerializer,
    BookDetailSerializer,
    BookListSerializer,
    BookSerializer,
)


class AuthorSerializerTests(TestCase):
    """
    Test suite for the AuthorSerializer.
    """
    def setUp(self):
        """
        Set up data for the AuthorSerializer tests.
        """
        self.author_data = {
            "first_name": "Test",
            "last_name": "Author",
            "pseudonym": "TA",
        }

    def test_serializer_with_valid_data(self):
        """
        Test that the AuthorSerializer is valid with proper data and correctly saves an Author instance.
        """
        serializer = AuthorSerializer(data=self.author_data)
        self.assertTrue(serializer.is_valid())
        author = serializer.save()
        self.assertEqual(author.first_name, self.author_data["first_name"])
        self.assertEqual(author.last_name, self.author_data["last_name"])

    def test_serializer_with_empty_pseudonym(self):
        """
        Test that the AuthorSerializer is valid even when the 'pseudonym' field is omitted.
        """
        data = self.author_data.copy()
        data.pop("pseudonym")
        serializer = AuthorSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class BookSerializerTests(TestCase):
    """
    Test suite for the Book-related serializers.
    """
    def setUp(self):
        """
        Set up data for the BookSerializer tests.
        """
        self.author = Author.objects.create(first_name="Test", last_name="Author")
        self.book_data = {
            "title": "Test Book",
            "author": self.author.id,
            "cover": "soft",
            "inventory": 5,
            "daily_fee": "10.50",
        }

    def test_book_serializer_with_valid_data(self):
        """
        Test that the BookSerializer is valid with proper data and correctly saves a Book instance.
        """
        serializer = BookSerializer(data=self.book_data)
        self.assertTrue(serializer.is_valid())
        book = serializer.save()
        self.assertEqual(book.title, self.book_data["title"])
        self.assertEqual(book.author.id, self.book_data["author"])

    def test_book_list_serializer(self):
        """
        Test that the BookListSerializer returns the correct serialized data for a Book instance.
        """
        book = Book.objects.create(
            title="Test Book",
            author=self.author,
            cover="soft",
            inventory=5,
            daily_fee="10.50",
        )
        serializer = BookListSerializer(book)
        data = serializer.data

        self.assertEqual(data["title"], book.title)
        self.assertEqual(data["author"]["first_name"], self.author.first_name)
        self.assertEqual(data["author"]["last_name"], self.author.last_name)

    def test_book_detail_serializer(self):
        """
        Test that the BookDetailSerializer returns the correct detailed serialized data for a Book instance.
        """
        book = Book.objects.create(
            title="Test Book",
            author=self.author,
            cover="soft",
            inventory=5,
            daily_fee="10.50",
        )
        serializer = BookDetailSerializer(book)
        data = serializer.data

        self.assertEqual(data["title"], book.title)
        self.assertEqual(data["inventory"], book.inventory)
        self.assertEqual(data["daily_fee"], "10.50")
        self.assertEqual(data["author"]["first_name"], self.author.first_name)

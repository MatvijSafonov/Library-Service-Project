from django.test import TestCase
from library.models import Author, Book
from library.serializers import (
    AuthorSerializer,
    BookSerializer,
    BookListSerializer,
    BookDetailSerializer,
)


class AuthorSerializerTests(TestCase):
    def setUp(self):
        self.author_data = {
            "first_name": "Test",
            "last_name": "Author",
            "pseudonym": "TA",
        }

    def test_serializer_with_valid_data(self):
        serializer = AuthorSerializer(data=self.author_data)
        self.assertTrue(serializer.is_valid())
        author = serializer.save()
        self.assertEqual(author.first_name, self.author_data["first_name"])
        self.assertEqual(author.last_name, self.author_data["last_name"])

    def test_serializer_with_empty_pseudonym(self):
        data = self.author_data.copy()
        data.pop("pseudonym")
        serializer = AuthorSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class BookSerializerTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name="Test", last_name="Author")
        self.book_data = {
            "title": "Test Book",
            "author": self.author.id,
            "cover": "soft",
            "inventory": 5,
            "daily_fee": "10.50",
        }

    def test_book_serializer_with_valid_data(self):
        serializer = BookSerializer(data=self.book_data)
        self.assertTrue(serializer.is_valid())
        book = serializer.save()
        self.assertEqual(book.title, self.book_data["title"])
        self.assertEqual(book.author.id, self.book_data["author"])

    def test_book_list_serializer(self):
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

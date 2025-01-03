from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.models import User
from .models import Author, Book
from .serializers import (AuthorSerializer,
                          BookSerializer,
                          BookListSerializer,
                          BookDetailSerializer)


class AuthorTestCase(TestCase):

    def setUp(self):
        self.author1 = Author.objects.create(first_name="John",
                                             last_name="Doe")
        self.author2 = Author.objects.create(first_name="Jane",
                                             last_name="Doe")
        self.author3 = Author.objects.create(first_name="John",
                                             last_name="Smith",
                                             pseudonym="Johnny")

    def test_full_name_method(self):
        """Test the full_name() method for the author"""
        self.assertEqual(self.author1.full_name(), "John Doe")
        self.assertEqual(self.author3.full_name(), "John Smith")

    def test_unique_constraint(self):
        """Test the uniqueness of first_name and last_name combination for authors"""
        with self.assertRaises(Exception):
            Author.objects.create(first_name="John", last_name="Doe")

    def test_author_serializer(self):
        """Test the author serialization using AuthorSerializer"""
        data = {
            "first_name": "George",
            "last_name": "Orwell",
            "pseudonym": "Eric Arthur Blair"
        }
        serializer = AuthorSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        author = serializer.save()
        self.assertEqual(author.first_name, "George")
        self.assertEqual(author.last_name, "Orwell")
        self.assertEqual(author.pseudonym, "Eric Arthur Blair")

    def test_author_api(self):
        """Test the API for creating and retrieving authors"""
        client = APIClient()
        url = reverse("library:author-list")
        response = client.post(url, {
            "first_name": "George",
            "last_name": "Orwell",
            "pseudonym": "Eric Arthur Blair"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)


class BookTestCase(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(email="admin@example.com",
                                                        password="admin123")
        self.regular_user = User.objects.create_user(email="user@example.com",
                                                     password="user123")

        self.author1 = Author.objects.create(first_name="John", last_name="Doe")
        self.book1 = Book.objects.create(
            title="Book One",
            author=self.author1,
            cover="soft",
            inventory=5,
            daily_fee=10.00
        )
        self.book2 = Book.objects.create(
            title="Book Two",
            author=self.author1,
            cover="hard",
            inventory=3,
            daily_fee=15.50
        )

    def test_book_serializer_with_permissions(self):
        """Test book serialization with permission checks"""
        data = {
            "title": "New Book",
            "author": self.author1.id,
            "cover": "hard",
            "inventory": 10,
            "daily_fee": 20.00
        }

        client = APIClient()
        client.force_authenticate(user=self.admin_user)
        serializer = BookSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        book = serializer.save()
        self.assertEqual(book.title, "New Book")
        self.assertEqual(book.author, self.author1)

        client.force_authenticate(user=self.regular_user)
        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_book_list_serializer_with_permissions(self):
        """Test the book list serialization with permission checks"""
        client = APIClient()

        client.force_authenticate(user=self.regular_user)
        serializer = BookListSerializer([self.book1, self.book2], many=True)
        self.assertEqual(len(serializer.data), 2)

        client.force_authenticate(user=None)
        response = client.get(reverse("library:book-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_book_detail_serializer_with_permissions(self):
        """Test the book detail serialization with permission checks"""
        client = APIClient()
        client.force_authenticate(user=self.admin_user)
        serializer = BookDetailSerializer(self.book1)
        self.assertEqual(serializer.data["title"], "Book One")
        self.assertEqual(serializer.data["inventory"], 5)

        client.force_authenticate(user=self.regular_user)
        response = client.get(reverse("library:book-detail", args=[self.book1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Book One")

        client.force_authenticate(user=None)
        response = client.get(reverse("library:book-detail", args=[self.book1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Book One")

    def test_book_api_create_with_permissions(self):
        """Test the API for creating a book with permission checks"""
        client = APIClient()
        client.force_authenticate(user=self.admin_user)
        url = reverse("library:book-list")
        response = client.post(url, {
            "title": "New API Book",
            "author": self.author1.id,
            "cover": "soft",
            "inventory": 10,
            "daily_fee": 18.00
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New API Book")

        client.force_authenticate(user=self.regular_user)
        response = client.post(url, {
            "title": "New API Book by User",
            "author": self.author1.id,
            "cover": "soft",
            "inventory": 10,
            "daily_fee": 18.00
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_api_list(self):
        """Test the API for retrieving a list of books"""
        client = APIClient()
        url = reverse("library:book-list")
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_book_api_retrieve(self):
        """Test the API for retrieving a book's details"""
        client = APIClient()
        url = reverse("library:book-detail", args=[self.book1.id])
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Book One")
        self.assertEqual(response.data["inventory"], 5)

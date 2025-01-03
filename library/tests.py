from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
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
        self.assertEqual(self.author1.full_name(), "John Doe")
        self.assertEqual(self.author3.full_name(), "John Smith")

    def test_unique_constraint(self):
        with self.assertRaises(Exception):
            Author.objects.create(first_name="John", last_name="Doe")

    def test_author_serializer(self):
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
        self.author1 = Author.objects.create(first_name="John",
                                             last_name="Doe")
        self.author2 = Author.objects.create(first_name="Jane",
                                             last_name="Doe")
        self.author3 = Author.objects.create(first_name="John",
                                             last_name="Smith",
                                             pseudonym="Johnny")

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
        self.book3 = Book.objects.create(
            title="Book Three",
            author=self.author2,
            cover="soft",
            inventory=2,
            daily_fee=12.00
        )

    def test_unique_constraint(self):
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Book One",
                author=self.author1,
                cover="hard",
                inventory=4,
                daily_fee=11.00
            )

    def test_book_serializer(self):
        data = {
            "title": "New Book",
            "author": self.author1.id,
            "cover": "hard",
            "inventory": 10,
            "daily_fee": 20.00
        }
        serializer = BookSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        book = serializer.save()
        self.assertEqual(book.title, "New Book")
        self.assertEqual(book.author, self.author1)
        self.assertEqual(book.inventory, 10)
        self.assertEqual(book.daily_fee, 20.00)

    def test_book_list_serializer(self):
        serializer = BookListSerializer([self.book1, self.book2, self.book3], many=True)
        self.assertEqual(len(serializer.data), 3)

    def test_book_detail_serializer(self):
        serializer = BookDetailSerializer(self.book1)
        self.assertEqual(serializer.data["title"], "Book One")
        self.assertEqual(serializer.data["inventory"], 5)

    def test_book_api_create(self):
        client = APIClient()
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

    def test_book_api_list(self):
        client = APIClient()
        url = reverse("library:book-list")
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_book_api_retrieve(self):
        client = APIClient()
        url = reverse("library:book-detail", args=[self.book1.id])
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Book One")
        self.assertEqual(response.data["inventory"], 5)

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from library.models import Author, Book
from django.contrib.auth import get_user_model

BOOKS_URL = reverse("library:book-list")
AUTHORS_URL = reverse("library:author-list")


def create_author(**params):
    defaults = {
        "first_name": "Test",
        "last_name": f"Author {Author.objects.count()}",
        "pseudonym": "TA",
    }
    defaults.update(params)
    return Author.objects.create(**defaults)


def create_book(**params):
    author = params.pop("author", None)
    if author is None:
        author = create_author()
    defaults = {
        "title": "Test Book",
        "author": author,
        "cover": "soft",
        "inventory": 5,
        "daily_fee": "10.50",
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def detail_url(book_id):
    return reverse("library:book-detail", args=[book_id])


class PublicBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateBookApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_books(self):
        create_book(title="First book")
        create_book(title="Second book")

        res = self.client.get(BOOKS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_create_book_forbidden_for_non_admin(self):
        author = create_author()
        payload = {
            "title": "Test Book",
            "author": author.id,
            "cover": "soft",
            "inventory": 5,
            "daily_fee": "10.50",
        }
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            email="admin@test.com", password="testpass123", is_staff=True
        )
        self.client.force_authenticate(self.admin)
        self.author = create_author()

    def test_create_book(self):
        payload = {
            "title": "Test Book",
            "author": self.author.id,
            "cover": "soft",
            "inventory": 5,
            "daily_fee": "10.50",
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data["id"])
        self.assertEqual(book.title, payload["title"])

    def test_partial_update_book(self):
        book = create_book(author=self.author)
        payload = {"title": "Updated title"}

        url = detail_url(book.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, payload["title"])

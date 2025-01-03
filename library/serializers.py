from rest_framework import serializers

from library.models import Book, Author


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = (
            "id",
            "first_name",
            "last_name",
            "pseudonym",
        )


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
        )


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "title",
            "author",
        )


class BookDetailSerializer(BookSerializer):
    class Meta:
        model = Book
        fields = (
            "title",
            "author",
            "inventory",
            "daily_fee",
        )


class BookBorrowingSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Book
        fields = ("id", "title", "author", "daily_fee")

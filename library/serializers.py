from rest_framework import serializers

from library.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "dayly_fee",
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
            "dayly_fee",
        )

from rest_framework import serializers

from library.models import Author, Book


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
    author = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
    )

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
    author = AuthorSerializer()

    class Meta:
        model = Book
        fields = (
            "title",
            "author",
        )


class BookDetailSerializer(BookSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Book
        fields = (
            "title",
            "author",
            "inventory",
            "daily_fee",
        )

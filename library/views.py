from rest_framework import viewsets

from library.models import Author, Book
from library.pagination import BookPagination
from library.permissions import IsAdminOrReadOnly
from library.serializers import (
    AuthorSerializer,
    BookDetailSerializer,
    BookListSerializer,
    BookSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = [BookPagination]

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        if self.action == "retrieve":
            return BookDetailSerializer
        return BookSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]

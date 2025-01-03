from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowing.views import BorrowingViewSet
from library.views import BookViewSet, AuthorViewSet

router = DefaultRouter()
router.register("books", BookViewSet)
router.register("authors", AuthorViewSet)
router.register("borrowing", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "library"

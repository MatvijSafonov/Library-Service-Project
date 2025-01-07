from django.urls import include, path
from rest_framework import routers

from borrowing.views import BorrowingViewSet

router = routers.DefaultRouter()
router.register("", BorrowingViewSet, basename="borrowing")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:pk>/return/",
        BorrowingViewSet.as_view({"post": "return_borrowing"}),
        name="borrowing-return",
    ),
]

app_name = "borrowing"


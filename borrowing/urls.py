from django.urls import include, path
from rest_framework import routers

from .views import BorrowingViewSet

router = routers.SimpleRouter()
router.register("", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "borrowing/<int:pk>/return_borrowing/",
        BorrowingViewSet.as_view({"post": "return_borrowing"}),
        name="return_borrowing"
    ),
]

app_name = "borrowing"

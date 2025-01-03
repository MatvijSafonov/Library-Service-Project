from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowing.views import BorrowingView

router = DefaultRouter()
router.register("", BorrowingView, basename="borrowing")


urlpatterns = router.urls

app_name = "borrowing"

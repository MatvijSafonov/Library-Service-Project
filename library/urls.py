from rest_framework.routers import DefaultRouter

from library.views import AuthorViewSet, BookViewSet

app_name = "library"

router = DefaultRouter()
router.register("books", BookViewSet)
router.register("authors", AuthorViewSet)

urlpatterns = router.urls

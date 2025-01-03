from django.urls import path
from rest_framework import routers

from payment.views import PaymentViewSet

app_name = "payment"

router = routers.DefaultRouter()
router.register("", PaymentViewSet, basename="payment")

urlpatterns = [
    path(
        "success/",
        PaymentViewSet.as_view({"get": "success"}),
        name="payment-success",
    ),
    path(
        "cancel/",
        PaymentViewSet.as_view({"get": "cancel"}),
        name="payment-cancel",
    ),
] + router.urls

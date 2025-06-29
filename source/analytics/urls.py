from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet, ClientDiscountViewSet

router = DefaultRouter()
router.register("products", ProductViewSet)
router.register("orders", OrderViewSet)
router.register("client-discounts", ClientDiscountViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

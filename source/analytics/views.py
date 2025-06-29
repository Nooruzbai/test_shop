from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
from users.models import ClientDiscount
from users.serializers import ClientDiscountSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Фильтр по статусу заказа. Например: PENDING, COMPLETED, CANCELLED.",
                type=openapi.TYPE_STRING,
                enum=[choice[0] for choice in Order.StatusChoices.choices],
            ),
            openapi.Parameter(
                "user_id",
                openapi.IN_QUERY,
                description="Фильтр по ID клиента (доступно только администраторам).",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "date_from",
                openapi.IN_QUERY,
                description="Дата начала периода для фильтрации (формат: YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "date_to",
                openapi.IN_QUERY,
                description="Дата конца периода для фильтрации (формат: YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            queryset = Order.objects.all()
        else:
            queryset = Order.objects.filter(user=user)

        status = self.request.GET.get("status")
        user_id = self.request.GET.get("user_id")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if status:
            queryset = queryset.filter(status__iexact=status)

        if user_id and user.is_staff:
            queryset = queryset.filter(user_id=user_id)

        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ClientDiscountViewSet(viewsets.ModelViewSet):
    queryset = ClientDiscount.objects.all()
    serializer_class = ClientDiscountSerializer
    permission_classes = [IsAuthenticated]

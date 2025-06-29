from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import CustomUserSerializer, HttpOnlyCookieTokenRefreshSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.response import Response
from dj_rest_auth.app_settings import api_settings as dj_rest_auth_app_settings
from dj_rest_auth.jwt_auth import set_jwt_access_cookie, set_jwt_refresh_cookie
from rest_framework import status


User = get_user_model()


class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "company_name",
                openapi.IN_QUERY,
                description="Фильтр по части названия компании (без учета регистра).",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Фильтр по статусу клиента ('true' для активных, 'false' для неактивных).",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "date_from",
                openapi.IN_QUERY,
                description="Дата регистрации 'от' (формат: YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "date_to",
                openapi.IN_QUERY,
                description="Дата регистрации 'до' (формат: YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        company = self.request.GET.get("company_name")
        status = self.request.GET.get("status")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if company:
            queryset = queryset.filter(company_name__icontains=company)

        if status is not None:
            is_active_status = status.lower() == "true"
            queryset = queryset.filter(is_active=is_active_status)

        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset.order_by("-created_at")


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = HttpOnlyCookieTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        response_data = {}
        response = Response(data=response_data, status=status.HTTP_200_OK)
        access_token = serializer.validated_data.get("access")
        refresh_token = serializer.validated_data.get("refresh")

        if access_token:
            set_jwt_access_cookie(response, access_token)

        if refresh_token:
            set_jwt_refresh_cookie(response, refresh_token)

        if not (
            dj_rest_auth_app_settings.JWT_AUTH_HTTPONLY
            and dj_rest_auth_app_settings.JWT_AUTH_COOKIE
        ):
            pass

        return response

from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView
from django.urls import path
from .views import CustomerListCreateView, CustomTokenRefreshView

urlpatterns = [
    # Ваши кастомные эндпоинты
    path("customers/", CustomerListCreateView.as_view(), name="customer-list-create"),
    # Группируем все, что связано с аутентификацией, под префиксом 'auth/'
    path("registration/", RegisterView.as_view(), name="rest_register"),
    # Путь для входа в систему
    path("login/", LoginView.as_view(), name="rest_login"),
    # Путь для выхода из системы
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path(
        "token/refresh/",
        CustomTokenRefreshView.as_view(),
        name="token_refresh",
    ),
]

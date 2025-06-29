from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .models import ClientDiscount
from rest_framework import serializers
from dj_rest_auth.serializers import JWTSerializer as BaseJWTSerializer
from dj_rest_auth.app_settings import api_settings as dj_rest_auth_api_settings
from django.conf import settings


User = get_user_model()


class ClientDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientDiscount
        fields = ["discount_percentage"]


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        label="Confirm password",
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "company_name",
            "phone",
            "created_at",
            "password",
            "password2",
        )
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        if attrs["password"] != attrs.get("password2"):
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2", None)
        user = User.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            password=validated_data["password"],
            # Pass any other optional fields like company_name or phone
            company_name=validated_data.get("company_name"),
            phone=validated_data.get("phone"),
        )
        return user


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    full_name = serializers.CharField(max_length=100)
    company_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20)

    def save(self, request):
        user = super().save(request)

        user.full_name = self.validated_data.get("full_name", "")
        user.company_name = self.validated_data.get("company_name", "")
        user.phone = self.validated_data.get("phone", "")

        user.save()

        return user

    def validate_email(self, email):
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                _("A user is already registered with this e-mail address.")
            )
        return email


class CustomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "company_name", "phone", "created_at")
        read_only_fields = ("id", "email", "created_at")


class CustomLoginJWTSerializer(BaseJWTSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Pop access token if JWT_AUTH_COOKIE is set and JWT_AUTH_HTTPONLY is True
        if (
            dj_rest_auth_api_settings.JWT_AUTH_COOKIE
            and dj_rest_auth_api_settings.JWT_AUTH_HTTPONLY
        ):
            if dj_rest_auth_api_settings.JWT_AUTH_COOKIE in data:
                data.pop(dj_rest_auth_api_settings.JWT_AUTH_COOKIE)
            if "access" in data:
                data.pop("access")

        if (
            dj_rest_auth_api_settings.JWT_AUTH_REFRESH_COOKIE
            and dj_rest_auth_api_settings.JWT_AUTH_HTTPONLY
        ):
            if dj_rest_auth_api_settings.JWT_AUTH_REFRESH_COOKIE in data:
                data.pop(dj_rest_auth_api_settings.JWT_AUTH_REFRESH_COOKIE)
            if "refresh" in data:
                data.pop("refresh")

        request = self.context.get("request")
        message = "Operation successful"

        if request:
            path = request.path
            if "login" in path:
                message = "Login successful"
            elif "registration" in path:
                message = "User registered successfully"

        data["message"] = message

        return data


class HttpOnlyCookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = serializers.CharField(
        read_only=True,
        help_text="This field is not used. The refresh token is taken from the HTTPOnly cookie named in settings.REST_AUTH['JWT_AUTH_REFRESH_COOKIE'].",
    )

    def validate(self, attrs):
        cookie_name = settings.REST_AUTH.get("JWT_AUTH_REFRESH_COOKIE")
        if not cookie_name:
            raise InvalidToken("Refresh cookie name not configured.")

        refresh_token_from_cookie = self.context["request"].COOKIES.get(cookie_name)

        if refresh_token_from_cookie is None:
            raise InvalidToken(
                f"The '{cookie_name}' HTTPOnly cookie was not found. "
                "Ensure it is being sent correctly with the request."
            )

        attrs_for_super_validation = {"refresh": refresh_token_from_cookie}
        validated_data = super().validate(attrs_for_super_validation)
        return validated_data

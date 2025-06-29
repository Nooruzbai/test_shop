from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.contrib.auth.models import PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, full_name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    full_name = models.CharField(max_length=100, verbose_name="Full Name")
    company_name = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Company Name"
    )
    phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Phone Number"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Registered")

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.full_name

    def get_full_name(self):
        return self.full_name

    class Meta:
        app_label = "users"


class ClientDiscount(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="client_discount"
    )
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Discount Percentage"
    )

    def __str__(self):
        return f"{self.user.full_name}: {self.discount_percentage}%"

    class Meta:
        verbose_name = "Client Discount"
        verbose_name_plural = "Client Discounts"

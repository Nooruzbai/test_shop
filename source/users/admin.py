from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ClientDiscount


class ClientDiscountInline(admin.StackedInline):
    model = ClientDiscount
    can_delete = False
    verbose_name_plural = "Client Discount"


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = (ClientDiscountInline,)

    list_display = ("email", "full_name", "company_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "full_name", "company_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("full_name", "company_name", "phone")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "password", "password2"),
            },
        ),
    )

    readonly_fields = ("last_login", "created_at")

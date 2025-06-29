from django.contrib import admin
from .models import Product, Order, OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    autocomplete_fields = ["product"]
    extra = 1
    readonly_fields = ("get_product_price",)

    @admin.display(description="Price (KZT)")
    def get_product_price(self, obj):
        if obj.product:
            return obj.product.price
        return "-"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderProductInline]
    list_display = ("id", "user", "status", "created_at", "total_amount")
    list_filter = ("status", "apply_vat", "created_at")
    search_fields = ("id", "user__email", "user__first_name", "user__last_name")
    readonly_fields = ("created_at", "total_amount")
    fieldsets = (
        ("Order Information", {"fields": ("user", "status", "created_at")}),
        (
            "Pricing & Delivery",
            {"fields": ("apply_vat", "delivery_cost", "total_amount")},
        ),
    )

    @admin.display(description="Total (KZT)")
    def total_amount(self, obj):
        return obj.calculate_total()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock_quantity", "is_active", "user")
    list_editable = ("price", "stock_quantity", "is_active")
    list_filter = ("is_active", "user")
    search_fields = ("name", "description", "user__email")
    fieldsets = (
        (None, {"fields": ("name", "description", "user")}),
        (
            "Pricing & Stock",
            {"fields": ("price", "stock_quantity", "discount_percentage", "is_active")},
        ),
    )

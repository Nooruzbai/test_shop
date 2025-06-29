from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from decimal import Decimal

User = get_user_model()


class Product(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="products", verbose_name="User"
    )
    name = models.CharField(max_length=200, verbose_name="Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Price (KZT)"
    )
    stock_quantity = models.PositiveIntegerField(
        default=0, verbose_name="Stock Quantity"
    )
    is_active = models.BooleanField(default=True, verbose_name="Available for Order")
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Product Discount Percentage",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        CONFIRMED = "confirmed", "Confirmed"
        SHIPPED = "shipped", "Shipped"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders", verbose_name="Client"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name="Status",
    )
    apply_vat = models.BooleanField(default=False, verbose_name="Apply 12% VAT")
    delivery_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Delivery Cost"
    )

    def __str__(self):
        return f"Order {self.id} by {self.user.full_name} ({self.status})"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def calculate_total(self):
        items_total = sum(op.quantity * op.product.price for op in self.products.all())
        client_discount = (
            self.user.client_discount.discount_percentage / 100
            if hasattr(self.user, "client_discount")
            else 0
        )
        product_discount = sum(
            op.quantity * op.product.price * (op.product.discount_percentage / 100)
            for op in self.products.all()
        )
        global_discount = 0.10 * items_total if items_total > 150000 else 0
        discounts = client_discount * items_total + product_discount + global_discount
        subtotal = items_total - discounts
        vat = Decimal('0.12') * subtotal if self.apply_vat else 0
        delivery = 0 if subtotal > 2000 else self.delivery_cost
        return subtotal + vat + delivery

    def clean(self):
        for op in self.products.all():
            if op.quantity > op.product.stock_quantity:
                raise ValidationError(
                    f"Not enough stock for {op.product.name}: {op.quantity} requested, {op.product.stock_quantity} available."
                )

    def save(self, *args, **kwargs):
        if self.status == "confirmed" and self.pk:
            original = Order.objects.get(pk=self.pk)
            if original.status != "confirmed":
                self.clean()
                for op in self.products.all():
                    product = op.product
                    product.stock_quantity -= op.quantity
                    product.save()
        super().save(*args, **kwargs)


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="products", verbose_name="Order"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="order_products",
        verbose_name="Product",
    )
    quantity = models.PositiveIntegerField(verbose_name="Quantity")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

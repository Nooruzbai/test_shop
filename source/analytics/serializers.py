from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Product, Order, OrderProduct

User = get_user_model()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "user",
            "name",
            "description",
            "price",
            "stock_quantity",
            "is_active",
            "discount_percentage",
        ]


class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    def validate(self, data):
        product = data["product"]
        quantity = data["quantity"]
        if not product.is_active:
            raise serializers.ValidationError(
                f"Product {product.name} is not available for order."
            )
        if quantity > product.stock_quantity:
            raise serializers.ValidationError(
                f"Not enough stock for {product.name}: {quantity} requested, {product.stock_quantity} available."
            )
        return data

    class Meta:
        model = OrderProduct
        fields = ["id", "product", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    products = OrderProductSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError("At least one product is required.")
        return value

    def create(self, validated_data):
        products_data = validated_data.pop("products")
        delivery_cost = validated_data.pop("delivery_cost", 200)
        order = Order.objects.create(delivery_cost=delivery_cost, **validated_data)
        for product_data in products_data:
            OrderProduct.objects.create(order=order, **product_data)
        order.total = order.calculate_total()
        order.save()
        return order

    def update(self, instance, validated_data):
        products_data = validated_data.pop("products", None)
        instance.user = validated_data.get("user", instance.user)
        instance.status = validated_data.get("status", instance.status)
        instance.apply_vat = validated_data.get("apply_vat", instance.apply_vat)
        instance.delivery_cost = validated_data.get(
            "delivery_cost", instance.delivery_cost
        )
        if products_data is not None:
            instance.products.all().delete()
            for product_data in products_data:
                OrderProduct.objects.create(order=instance, **product_data)
        instance.total = instance.calculate_total()
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["total"] = instance.calculate_total()
        return representation

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "created_at",
            "status",
            "apply_vat",
            "delivery_cost",
            "products",
            "total",
        ]

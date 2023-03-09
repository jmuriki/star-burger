from rest_framework import serializers
from .models import Product, Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(
        many=True,
        allow_empty=False,
        write_only=True,
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'products',
            'address',
            'firstname',
            'lastname',
            'phonenumber',
        ]

    def create(self, validated_data):
        order_items_payload = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for payload_item in order_items_payload:
            product = Product.objects.get(name=payload_item['product'])
            OrderItem.objects.create(
                order=order,
                product=payload_item['product'],
                quantity=payload_item['quantity'],
                price=product.price,
            )
        return order

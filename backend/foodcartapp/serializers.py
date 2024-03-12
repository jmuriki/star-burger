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
        order_items_validated_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        order_items = []
        for item_payload in order_items_validated_data:
            item_payload['order'] = order
            item_payload['price'] = Product.objects.get(
                name=item_payload['product']
            ).price
            order_items.append(OrderItem(**item_payload))
        OrderItem.objects.bulk_create(order_items)
        return order

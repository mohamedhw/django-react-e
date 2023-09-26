from dataclasses import fields
from rest_framework import serializers
from .models import Item, OrderItem, Order, BillingAddress



class CartItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.IntegerField()
    quantity = serializers.IntegerField()
    pic = serializers.ImageField()
    total = serializers.IntegerField()
    def to_representation(self, instance):
        return {
            'id': instance['id'],
            'name': instance['name'],
            'price': instance['price'],
            'quantity': instance['quantity'],
            'pic': instance['pic'],
            'total': instance['total'],
        }




class ItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"


class OrderItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['get_item_final_price']

class Task_extendedSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrderItem
        fields = ['price', 'name', 'quantity']

class TaskSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Order
        fields = ['get_total']

class JoinTaskSerializer(serializers.Serializer):
    model1 = Task_extendedSerializer(read_only=True)
    model2 = TaskSerializer(read_only=True)

    def to_representation(self, instance):
        model1 = OrderItem.objects.get(id=instance.id)
        model2 = Order.objects.get(id=instance.id)
        return {
            'model1': Task_extendedSerializer(model1).data,
            'model2': TaskSerializer(model2).data
        }



class OrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order

        fields = "__all__"


class BillingSerializers(serializers.ModelSerializer):
    class Meta:
        model = BillingAddress
        fields = "__all__"
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']
        

class MenuItemsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)
    category_id = serializers.IntegerField(write_only = True)
    
    class Meta:
        model = MenuItem
        fields = ['id','title', 'price','featured','category', 'category_id']
        

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        
class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemsSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id','user', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        read_only_fields = ['id', 'user', 'unit_price', 'price']
        

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemsSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity','unit_price', 'price']
        

class OrderSerializer(serializers.ModelSerializer):
    orderitem = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user','delivery_crew','status', 'total', 'date','order_item']
        read_only_fields = ['id', 'user', 'total', 'date']
        
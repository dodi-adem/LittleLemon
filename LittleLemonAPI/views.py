from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import MenuItem,Cart
from .serializer import MenuItemsSerializer, UserSerializer, CartSerializer

# Create your views here.
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()
    
class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='Manager').exists():
            return False
        if request.user.groups.filter(name='Delivery crew').exists():
            return False
        return True

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemsSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManager()]
    

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemsSerializer
    
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManager()]
    
    
class ManagerUsersView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), IsManager()]
    
    def get(self, request):
        managers = User.objects.filter(groups__name='Manager')
        serialized_item = UserSerializer(managers, many = True)
        return Response(serialized_item.data,status=status.HTTP_200_OK)
    
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'message':'user_id is required'},status = status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'user not found'}, status = status.HTTP_404_NOT_FOUND)
        
        
        manager_group,created = Group.objects.get_or_create(name = 'Manager')
        manager_group.user_set.add(user)
        return Response({'message': 'user added to manager group'}, status=status.HTTP_201_CREATED)
      
class SingleManagerUserView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), IsManager()]
    
    def delete(self,request,user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message':'user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            manager_group = Group.objects.get(name='Manager')
        except Group.DoesNotExist:
            return Response({'message': 'Manager group not found'}, status=status.HTTP_404_NOT_FOUND)
        if manager_group in user.groups.all():
            manager_group.user_set.remove(user)
            return Response({'message': 'user removed from Manager group'}, status=status.HTTP_200_OK)  
        else:
            return Response({'message':'user not in manager group'}, status=status.HTTP_400_BAD_REQUEST)

class DeliveryCrewUserView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), IsManager()]
    
    def get(self, request):
        delivery_crew = User.objects.filter(groups__name='Delivery crew')
        serialized_item = UserSerializer(delivery_crew, many=True)
        return Response(serialized_item.data, status = status.HTTP_200_OK)
    
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'message':'user_id is required'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message':'user not found'},status = status.HTTP_404_NOT_FOUND)
        
        delivery_group,created = Group.objects.get_or_create(name='Delivery crew')
        delivery_group.user_set.add(user)
        return Response({'message':"user added to Delivery crew group"}, status=status.HTTP_201_CREATED)
        
class singleDeliveryCrewUserView(APIView):
    def get_permissons(self):
        return [IsAuthenticated(), IsManager()]
    
    def delete(self,request,user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message':'user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            delivery_group = Group.objects.get(name='Delivery crew')
        except Group.DoesNotExist:
            return Response({'message':'Delivery crew group not found'}, status=status.HTTP_404_NOT_FOUND)
        if delivery_group in user.groups.all():
            delivery_group.user_set.remove(user)
            return Response({'message':'user removed from Delivery crew group'}, status=status.HTTP_200_OK)
        else:
            return Response({'message':'user is not in Delivery group'}, status=status.HTTP_400_BAD_REQUEST)
        
class CartView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), IsCustomer()]
    def get(self,request):
        cart = Cart.objects.filter(user=request.user)
        serialized_cart = CartSerializer(cart,many=True)
        return Response(serialized_cart.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        menuitem_id = request.data.get('menuitem_id')
        quantity = request.data.get('quantity')
        
        if not menuitem_id or not quantity:
            return Response({'message':'menuitem_id and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quantity = int(quantity)
        except ValueError:
            return Response({'message': 'quantity must be integer'}, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity <= 0 :
            return Response({'message': 'quantity must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            menuitem = MenuItem.objects.get(id=menuitem_id)
        except MenuItem.DoesNotExist:
            return Response({'message':'menuitem not found'}, status=status.HTTP_404_NOT_FOUND)
        
        unit_price = menuitem.price
        
        try:
            cart_item = Cart.objects.get(user=request.user, menuitem=menuitem)
            cart_item.quantity += quantity
            cart_item.price = cart_item.unit_price * cart_item.quantity
            cart_item.save()
        except Cart.DoesNotExist:
            total_price = quantity * unit_price
            cart_item = Cart.objects.create(
                user=request.user,
                menuitem = menuitem,
                unit_price = unit_price,
                quantity=quantity,
                price=total_price
            )
        
        serialized_item = CartSerializer(cart_item)
        return Response(serialized_item.data, status=status.HTTP_201_CREATED)
    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({'message': 'all cart items deleted'}, status=status.HTTP_200_OK)
        
from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('groups/manager/users', views.ManagerUsersView.as_view()),
    path('groups/manager/users/<int:user_id>', views.SingleManagerUserView.as_view()),
    path('groups/delivery-crew/users', views.DeliveryCrewUserView.as_view()),
    path('groups/delivery-crew/users/<int:user_id>', views.singleDeliveryCrewUserView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
]
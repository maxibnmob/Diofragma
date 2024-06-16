from django.urls import path,include
from .views import *


urlpatterns = [
    path('', index, name='home'),
    path('catalog/', catalog, name='catalog'),
    path('category/<int:cat_id>/', category, name='category'),
    path('product/<int:product_id>/', product, name='product'),
    path('cart/', cart, name='cart'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('order/', order, name='order'),
    path('order_menu/', order_menu, name='order_menu'),
    path('order_add/<int:product_id>/', order_add, name='order_add'),
    path('order_detail/', order_detail, name='order_detail'),
    path('about/', about, name='about'),
    path('wherefind/', wherefind, name='wherefind'),
    path('', include('django.contrib.auth.urls')),
    path('register/', Register.as_view(), name = 'register'),
]

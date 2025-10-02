from django.urls import path
from .views import (
    ProductListView, ProductDetailView, CartView, FavouriteView, OrderListView, OrderDetailView,
    ShippingUpdateView, PaymentUpdateView
)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='products'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('favourites/', FavouriteView.as_view(), name='favourites'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:order_id>/shipping/', ShippingUpdateView.as_view(), name='shipping_update'),
    path('orders/<int:order_id>/payment/', PaymentUpdateView.as_view(), name='payment_update'),
]

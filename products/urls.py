from django.urls import path
from .views import (
    ProductListView, ProductDetailView, CartView, FavouriteView, OrderListView, OrderDetailView,
    ShippingUpdateView, PaymentUpdateView, AddToCartView, AddToFavouriteView, RemoveCartItemView, RemoveFavouriteView,
    UpdateCartItemView
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
    path('cart/add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('favourites/add/<int:product_id>/', AddToFavouriteView.as_view(), name='add_to_favourite'),
    path('cart/remove/<int:item_id>/', RemoveCartItemView.as_view(), name='remove_cart_item'),
    path('favourites/remove/<int:fav_id>/', RemoveFavouriteView.as_view(), name='remove_favourite'),
    path('cart/update/<int:item_id>/<str:action>/', UpdateCartItemView.as_view(), name='update_cart_item'),

]

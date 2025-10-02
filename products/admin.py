from django.contrib import admin
from .models import (
    Product, Cart, CartItem, Favourite, Review,
    Order, OrderItem, Shipping, Payment, Menu
)

# ---------- Product ----------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock')
    search_fields = ('name', 'description')
    list_filter = ('name','price')
    # ordering = ('-created_at',)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id','name','parent')
    list_filter = ('name',)

# ---------- Cart ----------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    search_fields = ('user__username', 'user__email')
    list_filter = ('user',)
    inlines = [CartItemInline]


# ---------- Favourite ----------
@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product')
    search_fields = ('user__username', 'product__name')
    list_filter = ('user','product')


# ---------- Review ----------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'rating')
    search_fields = ('user__username', 'product__name', 'comment')
    list_filter = ('rating', 'user', 'product')


# ---------- Order ----------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount')
    search_fields = ('user__username', 'user__email')
    list_filter = ('status',)
    inlines = [OrderItemInline]


# ---------- Shipping ----------
@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'city', 'state', 'postal_code')
    search_fields = ('order__id', 'address', 'city', 'state', 'postal_code')
    list_filter = ('city', 'state')


# ---------- Payment ----------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'method', 'status')
    search_fields = ('order__id', 'method')
    list_filter = ('method', 'status')

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import (
    Product, Cart, CartItem, Favourite,
    Review, Order, OrderItem, Shipping, Payment, Menu
)
from django.db import transaction

# --- PRODUCTS ---
class ProductListView(View):
    template_name = "products_list.html"

    def get(self, request):
        products = Product.objects.all()
        return render(request, self.template_name, {"products": products})

    def post(self, request):
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock', 0)
        description = request.POST.get('description', '')

        if not name or not price:
            messages.error(request, "Name and price required")
            return redirect('products')

        Product.objects.create(name=name, price=price, stock=stock, description=description)
        messages.success(request, "Product created successfully")
        return redirect('products')


class ProductDetailView(View):
    template_name = "product_detail.html"

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return render(request, self.template_name, {"product": product})


# --- CART ---
class CartView(LoginRequiredMixin, View):
    template_name = "cart.html"
    login_url = "login"

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = CartItem.objects.filter(cart=cart).select_related('product')
        return render(request, self.template_name, {"cart": cart, "items": items})

    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=product_id)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()
        messages.success(request, "Added to cart")
        return redirect('cart')


# --- FAVOURITES ---
class FavouriteView(LoginRequiredMixin, View):
    template_name = "favourites.html"
    login_url = "login"

    def get(self, request):
        favs = Favourite.objects.filter(user=request.user).select_related('product')
        return render(request, self.template_name, {"favs": favs})

    def post(self, request):
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        Favourite.objects.get_or_create(user=request.user, product=product)
        messages.success(request, "Added to favourites")
        return redirect('favourites')
    
# --- Orders List ---
class OrderListView(LoginRequiredMixin, View):
    template_name = "orders/order_list.html"

    def get(self, request):
        orders = Order.objects.filter(user=request.user).select_related('shipping', 'payment')
        return render(request, self.template_name, {'orders': orders})


# --- Order Detail ---
class OrderDetailView(LoginRequiredMixin, View):
    template_name = "orders/order_detail.html"

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        items = order.items.select_related('product')
        return render(request, self.template_name, {
            'order': order,
            'items': items,
            'shipping': getattr(order, 'shipping', None),
            'payment': getattr(order, 'payment', None)
        })


# --- Shipping Update ---
class ShippingUpdateView(LoginRequiredMixin, View):
    template_name = "orders/shipping_form.html"

    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, user=request.user)
        shipping = getattr(order, 'shipping', None)
        return render(request, self.template_name, {'order': order, 'shipping': shipping})

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, user=request.user)
        data = request.POST
        Shipping.objects.update_or_create(
            order=order,
            defaults={
                'full_name': data.get('full_name'),
                'address_line1': data.get('address_line1'),
                'address_line2': data.get('address_line2'),
                'city': data.get('city'),
                'state': data.get('state'),
                'postal_code': data.get('postal_code'),
                'country': data.get('country'),
                'phone': data.get('phone'),
            }
        )
        return redirect('order_detail', pk=order.id)


# --- Payment Update ---
class PaymentUpdateView(LoginRequiredMixin, View):
    template_name = "orders/payment_form.html"

    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, user=request.user)
        payment = getattr(order, 'payment', None)
        return render(request, self.template_name, {'order': order, 'payment': payment})

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, user=request.user)
        method = request.POST.get('method')
        Payment.objects.update_or_create(
            order=order,
            defaults={'method': method, 'status': 'pending'}
        )
        return redirect('order_detail', pk=order.id)

class DashboardView(View):
    template_name = "dashboard.html"

    def get(self, request):
        menus = Menu.objects.filter(parent__isnull=True).prefetch_related('children')
        recently_added = Product.objects.order_by('-id')[:8]  # last 8 products
        best_sellers = Product.objects.order_by('-stock')[:8]  # placeholder: you can calculate based on sales
        reviews = Review.objects.select_related('user', 'product').order_by('-id')[:10]

        return render(request, self.template_name, {
            'menus': menus,
            'recently_added': recently_added,
            'best_sellers': best_sellers,
            'reviews': reviews,
        })
        

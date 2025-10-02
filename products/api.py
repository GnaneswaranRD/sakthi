from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import (
    Product, Cart, CartItem, Favourite,
    Review, Order, OrderItem, Shipping, Payment
)
from django.db import transaction
from decimal import Decimal

# --- PRODUCTS ---
class ProductListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        products = Product.objects.all().values()
        return Response(list(products))

    def post(self, request):
        name = request.data.get('name')
        price = request.data.get('price')
        stock = request.data.get('stock', 0)
        description = request.data.get('description', '')

        if not name or not price:
            return Response({'error': 'Name and price required'}, status=400)

        product = Product.objects.create(
            name=name, price=price, stock=stock, description=description
        )
        return Response({'id': product.id, 'message': 'Product created'}, status=201)


class ProductDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return Response({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'stock': product.stock,
            'description': product.description
        })


# --- CART ---
class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = CartItem.objects.filter(cart=cart).select_related('product')
        return Response({
            'cart_id': cart.id,
            'items': [
                {
                    'id': i.id,
                    'product_id': i.product.id,
                    'product_name': i.product.name,
                    'quantity': i.quantity
                } for i in items
            ]
        })

    def post(self, request):
        """Add item to cart"""
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=product_id)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()
        return Response({'message': 'Added to cart'})


# --- FAVOURITES ---
class FavouriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        favs = Favourite.objects.filter(user=request.user).select_related('product')
        return Response([
            {
                'id': f.id,
                'product_id': f.product.id,
                'product_name': f.product.name
            } for f in favs
        ])

    def post(self, request):
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        Favourite.objects.get_or_create(user=request.user, product=product)
        return Response({'message': 'Added to favourites'})

    def delete(self, request):
        product_id = request.data.get('product_id')
        Favourite.objects.filter(user=request.user, product_id=product_id).delete()
        return Response({'message': 'Removed from favourites'})


# --- REVIEWS ---
class ReviewView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id).select_related('user')
        return Response([
            {
                'user': r.user.username,
                'rating': r.rating,
                'comment': r.comment
            } for r in reviews
        ])

    def post(self, request, product_id):
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        Review.objects.create(
            user=request.user, product_id=product_id,
            rating=rating, comment=comment
        )
        return Response({'message': 'Review added'})


# --- ORDERS ---
class OrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        return Response([
            {
                'id': o.id,
                'status': o.status,
                'total_amount': o.total_amount,
                'created_at': o.created_at
            } for o in orders
        ])

    @transaction.atomic
    def post(self, request):
        """Create order from cart items"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = CartItem.objects.filter(cart=cart).select_related('product')
        if not items:
            return Response({'error': 'Cart is empty'}, status=400)

        total = sum([i.product.price * i.quantity for i in items])
        order = Order.objects.create(user=request.user, total_amount=total)

        for i in items:
            OrderItem.objects.create(
                order=order,
                product=i.product,
                quantity=i.quantity,
                price=i.product.price
            )
            # reduce stock
            i.product.stock -= i.quantity
            i.product.save()

        items.delete()  # clear cart
        return Response({'order_id': order.id, 'total': total})


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        items = order.items.select_related('product')
        return Response({
            'id': order.id,
            'status': order.status,
            'total_amount': order.total_amount,
            'items': [
                {
                    'product': it.product.name,
                    'quantity': it.quantity,
                    'price': it.price
                } for it in items
            ]
        })


# --- SHIPPING ---
class ShippingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        data = request.data
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
        return Response({'message': 'Shipping info saved'})


# --- PAYMENT ---
class PaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        method = request.data.get('method', 'cod')
        Payment.objects.update_or_create(
            order=order,
            defaults={'method': method, 'status': 'pending'}
        )
        return Response({'message': 'Payment initiated'})

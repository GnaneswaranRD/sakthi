from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Menu, Product, Review


# REGISTER VIEW
class RegisterView(View):
    template_name = "register.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        User.objects.create_user(username=email, email=email, password=password)
        messages.success(request, "Registration successful. Please log in.")
        return redirect('login')


# LOGIN VIEW
class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    
class DashboardView(View):
    template_name = "dashboard.html"
    login_url = reverse_lazy('login')

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


# LOGOUT VIEW
class LogoutView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request):
        logout(request)
        messages.info(request, "Logged out successfully")
        return redirect('login')
    
    


class ProfileView(LoginRequiredMixin, View):
    template_name = "profile.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        user = request.user
        profile = user.profile

        # Update user fields
        # user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)
        user.save()

        # Update profile fields
        profile.full_name = request.POST.get("full_name", profile.full_name)
        profile.phone = request.POST.get("phone", profile.phone)
        profile.address = request.POST.get("address", profile.address)

        if "profile_pic" in request.FILES:
            profile.profile_pic = request.FILES["profile_pic"]

        profile.save()

        messages.success(request, "Profile updated successfully")
        return redirect("profile")

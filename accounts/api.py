from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin



# REGISTER
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    
    @swagger_auto_schema(
        operation_description="Create new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='email'),
                'password': openapi.Schema(type=openapi.TYPE_NUMBER, description='password'),
            },
            required=['email', 'password']
        ),
        responses={201: openapi.Response('user created')}
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if User.objects.filter(username=email).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=email, email=email, password=password)

        # get token
        token, created = Token.objects.get_or_create(user=user)

        # use .values() to return minimal user info
        user_data = User.objects.filter(id=user.id).values('id', 'username', 'email').first()

        return Response({
            "user": user_data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)


# LOGIN
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=user)

        # use .values() to return user data
        user_data = User.objects.filter(id=user.id).values('id', 'username', 'email').first()

        return Response({
            "user": user_data,
            "token": token.key
        })


# LOGOUT
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # delete the token
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
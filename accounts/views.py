from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from .models import HRUser
from .serializers import (
    HRUserSerializer,
    HRUserCreateSerializer,
    LoginSerializer,
    HRUserProfileSerializer
)
from drf_spectacular.utils import extend_schema


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        operation_id="login",
        summary="User Login",
        description="Login with email and password",
        request=LoginSerializer,
        tags=['Authentication']
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
                     
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': HRUserProfileSerializer(user).data,
                'message': 'Login successful!'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        operation_id="profile",
        summary="User Profile",
        description="Get the profile information of the logged-in user",
        responses=HRUserProfileSerializer,
        tags=['Authentication']
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        serializer = HRUserProfileSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        operation_id="session_login",
        summary="Session Login",
        description="Login with session authentication for Swagger UI",
        request=LoginSerializer,
        responses={
            200: {
                "description": "Successful login"
            },
            400: {
                "description": "Invalid credentials"
            }
        },
        tags=['Authentication']
    )
    @action(detail=False, methods=['post'])
    def session_login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return Response({
                'message': 'Login successful!',
                'user': HRUserProfileSerializer(user).data
            })
        
        return Response({
            'error': 'Invalid username or password!'
        }, status=status.HTTP_400_BAD_REQUEST)



class HRUserViewSet(viewsets.ModelViewSet):
    queryset = HRUser.objects.all()
    serializer_class = HRUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_staff', 'hr_company']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'created_at', 'last_login']
    ordering = ['-created_at']
    
    @extend_schema(
        operation_id="list_hr_users",
        summary="List Users",
        description="Lists all Users",
        tags=['Users']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="create_hr_user",
        summary="Create User",
        description="Creates a new User",
        tags=['Users']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="retrieve_hr_user",
        summary="Retrieve User",
        description="Get the details of an User",
        tags=['Users']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="update_hr_user",
        summary="Update User",
        description="Updates the information of an User",
        tags=['Users']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="partial_update_hr_user",
        summary="Partially Update User",
        description="Partially updates the information of an User",
        tags=['Users']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="delete_hr_user",
        summary="Delete User",
        description="Deletes an User",
        tags=['Users']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, 'hr_company'):
                queryset = queryset.filter(hr_company=self.request.user.hr_company)
            else:
                queryset = queryset.none()
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HRUserCreateSerializer
        return HRUserSerializer
    
    @extend_schema(
        operation_id="my_profile",
        summary="My Profile",
        description="Get the profile information of the logged in user",
        responses=HRUserProfileSerializer,
        tags=['Users']
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = HRUserProfileSerializer(request.user)
        return Response(serializer.data)


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'accounts/login.html')
    
    @method_decorator(csrf_protect)
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            return render(request, 'accounts/login.html')
        
        user = authenticate(request, username=email, password=password)
        
        if user and user.is_active:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
            return render(request, 'accounts/login.html')


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        return render(request, 'accounts/dashboard.html', {
            'user': request.user
        })


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')
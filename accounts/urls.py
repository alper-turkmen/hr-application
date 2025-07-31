from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HRUserViewSet, AuthViewSet, LoginView, DashboardView, logout_view

router = DefaultRouter()
router.register(r'users', HRUserViewSet, basename='hruser')
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    # API routes
    path('', include(router.urls)),
    
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('logout/', logout_view, name='logout'),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HRUserViewSet, AuthViewSet

router = DefaultRouter()
router.register(r'users', HRUserViewSet, basename='hruser')
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]
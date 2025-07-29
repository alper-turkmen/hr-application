from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HRCompanyViewSet, CustomerCompanyViewSet

router = DefaultRouter()
router.register(r'hr-companies', HRCompanyViewSet, basename='hrcompany')
router.register(r'customer-companies', CustomerCompanyViewSet, basename='customercompany')

urlpatterns = [
    path('', include(router.urls)),
]
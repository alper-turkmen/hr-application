from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema
from .models import HRCompany, CustomerCompany
from .serializers import (
    HRCompanySerializer,
    CustomerCompanySerializer,
    HRCompanySimpleSerializer,
    CustomerCompanySimpleSerializer
)

class HRCompanyViewSet(viewsets.ModelViewSet):
    queryset = HRCompany.objects.all()
    serializer_class = HRCompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    @extend_schema(
        operation_id="list_hr_companies",
        tags=['HR Companies']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="create_hr_company",
        summary="HR Şirketi Oluştur",
        description="Yeni HR şirketi oluşturur",
        tags=['HR Companies']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="retrieve_hr_company",
        summary="HR Şirketi Detayı",
        description="HR şirketi detayını getirir",
        tags=['HR Companies']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="update_hr_company",
        summary="HR Şirketi Güncelle",
        description="HR şirketi bilgilerini günceller",
        tags=['HR Companies']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="partial_update_hr_company",
        summary="HR Şirketi Kısmi Güncelle",
        description="HR şirketi bilgilerini kısmen günceller",
        tags=['HR Companies']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="delete_hr_company",
        summary="HR Şirketi Sil",
        description="HR şirketini siler",
        tags=['HR Companies']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, 'hr_company'):
                queryset = queryset.filter(id=self.request.user.hr_company.id)
            else:
                queryset = queryset.none()
        
        return queryset
    
    @extend_schema(
        operation_id="hr_companies_simple_list",
        summary="HR Şirketleri Basit Liste",
        description="Aktif HR şirketlerinin basit listesini getirir",
        responses=HRCompanySimpleSerializer(many=True),
        tags=['HR Companies']
    )
    @action(detail=False, methods=['get'])
    def simple_list(self, request):
        queryset = self.get_queryset().filter(is_active=True)
        serializer = HRCompanySimpleSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        operation_id="toggle_hr_company_active",
        summary="HR Şirketi Aktiflik Durumu Değiştir",
        description="HR şirketinin aktiflik durumunu değiştirir",
        tags=['HR Companies']
    )
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        company = self.get_object()
        company.is_active = not company.is_active
        company.save()
        
        serializer = self.get_serializer(company)
        return Response({
            'message': f'Şirket {"aktif" if company.is_active else "pasif"} yapıldı.',
            'data': serializer.data
        })

class CustomerCompanyViewSet(viewsets.ModelViewSet):
    queryset = CustomerCompany.objects.all()
    serializer_class = CustomerCompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    @extend_schema(
        operation_id="list_customer_companies",
        summary="Müşteri Şirketleri Listele",
        description="Müşteri şirketlerini listeler",
        tags=['Customer Companies']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="create_customer_company",
        summary="Müşteri Şirketi Oluştur",
        description="Yeni müşteri şirketi oluşturur",
        tags=['Customer Companies']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="retrieve_customer_company",
        summary="Müşteri Şirketi Detayı",
        description="Müşteri şirketi detayını getirir",
        tags=['Customer Companies']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="update_customer_company",
        summary="Müşteri Şirketi Güncelle",
        description="Müşteri şirketi bilgilerini günceller",
        tags=['Customer Companies']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="partial_update_customer_company",
        summary="Müşteri Şirketi Kısmi Güncelle",
        description="Müşteri şirketi bilgilerini kısmen günceller",
        tags=['Customer Companies']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        operation_id="delete_customer_company",
        summary="Müşteri Şirketi Sil",
        description="Müşteri şirketini siler",
        tags=['Customer Companies']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, 'authorized_customer_companies'):
                authorized_ids = self.request.user.authorized_customer_companies.values_list('id', flat=True)
                queryset = queryset.filter(id__in=authorized_ids)
            else:
                queryset = queryset.none()
        
        return queryset
    
    @extend_schema(
        operation_id="customer_companies_simple_list",
        summary="Müşteri Şirketleri Basit Liste",
        description="Aktif müşteri şirketlerinin basit listesini getirir",
        responses=CustomerCompanySimpleSerializer(many=True),
        tags=['Customer Companies']
    )
    @action(detail=False, methods=['get'])
    def simple_list(self, request):
        queryset = self.get_queryset().filter(is_active=True)
        serializer = CustomerCompanySimpleSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        operation_id="my_authorized_customer_companies",
        summary="Yetkilendirilmiş Şirketlerim",
        description="Kullanıcının yetkilendirildiği müşteri şirketlerini getirir",
        responses=CustomerCompanySimpleSerializer(many=True),
        tags=['Customer Companies']
    )
    @action(detail=False, methods=['get'])
    def my_authorized(self, request):
        if hasattr(request.user, 'authorized_customer_companies'):
            companies = request.user.get_authorized_customer_companies()
            serializer = CustomerCompanySimpleSerializer(companies, many=True)
            return Response(serializer.data)
        return Response([])
    
    @extend_schema(
        operation_id="toggle_customer_company_active",
        summary="Müşteri Şirketi Aktiflik Durumu Değiştir",
        description="Müşteri şirketinin aktiflik durumunu değiştirir",
        tags=['Customer Companies']
    )
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        company = self.get_object()
        company.is_active = not company.is_active
        company.save()
        
        serializer = self.get_serializer(company)
        return Response({
            'message': f'Müşteri şirketi {"aktif" if company.is_active else "pasif"} yapıldı.',
            'data': serializer.data
        })
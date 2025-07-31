from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import JobPosting
from .serializers import JobPostingSerializer, JobPostingCreateSerializer
from common.permissions import IsHRUserPermission, CustomerCompanyPermission, HRCompanyPermission

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    permission_classes = [IsHRUserPermission, CustomerCompanyPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'customer_company', 'hr_company']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return JobPosting.objects.all()
        
        return JobPosting.objects.filter(
            hr_company=user.hr_company,
            customer_company__in=user.get_authorized_customer_companies()
        )
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return JobPostingCreateSerializer
        return JobPostingSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            hr_company=self.request.user.hr_company
        )
    
    @action(detail=False, methods=['get'])
    def my_postings(self, request):
        queryset = self.get_queryset().filter(created_by=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active_postings(self, request):
        queryset = self.get_queryset().filter(status='active', is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        job_posting = self.get_object()
        job_posting.status = 'inactive'
        job_posting.save()
        serializer = self.get_serializer(job_posting)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        job_posting = self.get_object()
        job_posting.status = 'active'
        job_posting.save()
        serializer = self.get_serializer(job_posting)
        return Response(serializer.data)

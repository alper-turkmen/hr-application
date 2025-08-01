import logging
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import JobPosting
from .serializers import JobPostingSerializer, JobPostingCreateSerializer
from common.permissions import IsHRUserPermission, CustomerCompanyPermission, HRCompanyPermission

logger = logging.getLogger('wisehire.jobs')

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
        job_posting = serializer.save(
            created_by=self.request.user,
            hr_company=self.request.user.hr_company
        )
        
        logger.info(f"Job posting created - Title: {job_posting.title}, Code: {job_posting.code}, "
                   f"Customer Company: {job_posting.customer_company.name}, "
                   f"Created by: {self.request.user.username} (ID: {self.request.user.id})")
    
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
        old_status = job_posting.status
        job_posting.status = 'inactive'
        job_posting.save()
        
        logger.info(f"Job posting deactivated - Title: {job_posting.title}, Code: {job_posting.code}, "
                   f"Status changed from '{old_status}' to 'inactive', "
                   f"Deactivated by: {request.user.username} (ID: {request.user.id})")
        
        serializer = self.get_serializer(job_posting)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        job_posting = self.get_object()
        old_status = job_posting.status
        job_posting.status = 'active'
        job_posting.save()
        
        logger.info(f"Job posting activated - Title: {job_posting.title}, Code: {job_posting.code}, "
                   f"Status changed from '{old_status}' to 'active', "
                   f"Activated by: {request.user.username} (ID: {request.user.id})")
        
        serializer = self.get_serializer(job_posting)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {
            'title': instance.title,
            'status': instance.status,
            'closing_date': instance.closing_date
        }
        response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            logger.info(f"Job posting updated - Title: {instance.title}, Code: {instance.code}, "
                       f"Updated by: {request.user.username} (ID: {request.user.id}), "
                       f"Changes: {request.data}")
        return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        job_info = f"Title: {instance.title}, Code: {instance.code}, ID: {instance.id}"
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            logger.warning(f"Job posting deleted - {job_info}, "
                          f"Deleted by: {request.user.username} (ID: {request.user.id})")
        return response

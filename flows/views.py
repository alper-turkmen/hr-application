import logging
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import ActivityType, Status, CandidateFlow, Activity
from .serializers import (
    ActivityTypeSerializer, StatusSerializer, CandidateFlowSerializer,
    CandidateFlowCreateSerializer, CandidateFlowListSerializer,
    ActivitySerializer, ActivityCreateSerializer
)
from common.permissions import IsHRUserPermission, CustomerCompanyPermission, HRCompanyPermission

logger = logging.getLogger('wisehire.flows')

class ActivityTypeViewSet(viewsets.ModelViewSet):
    queryset = ActivityType.objects.filter(is_active=True)
    serializer_class = ActivityTypeSerializer
    permission_classes = [IsHRUserPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']

class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.filter(is_active=True)
    serializer_class = StatusSerializer
    permission_classes = [IsHRUserPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activity_type', 'is_active']
    
    @action(detail=False, methods=['get'])
    def by_activity_type(self, request):
        activity_type_id = request.query_params.get('activity_type_id')
        if not activity_type_id:
            return Response({'error': 'activity_type_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        statuses = Status.objects.filter(
            activity_type_id=activity_type_id,
            is_active=True
        )
        serializer = self.get_serializer(statuses, many=True)
        return Response(serializer.data)

class CandidateFlowViewSet(viewsets.ModelViewSet):
    queryset = CandidateFlow.objects.all()
    serializer_class = CandidateFlowSerializer
    permission_classes = [IsHRUserPermission, CustomerCompanyPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['flow_status', 'job_posting', 'candidate', 'hr_company']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = CandidateFlow.objects.all()
        else:
            queryset = CandidateFlow.objects.filter(
                hr_company=user.hr_company,
                job_posting__customer_company__in=user.get_authorized_customer_companies()
            )
        
        job_code = self.request.query_params.get('job_code', None)
        if job_code:
            queryset = queryset.filter(job_posting__code__icontains=job_code)
        
        job_title = self.request.query_params.get('job_title', None)
        if job_title:
            queryset = queryset.filter(job_posting__title__icontains=job_title)
        
        candidate_search = self.request.query_params.get('candidate_search', None)
        if candidate_search:
            queryset = queryset.filter(
                Q(candidate__first_name__icontains=candidate_search) |
                Q(candidate__last_name__icontains=candidate_search) |
                Q(candidate__email__icontains=candidate_search)
            )
        
        candidate_phone = self.request.query_params.get('candidate_phone', None)
        if candidate_phone:
            queryset = queryset.filter(candidate__phone__icontains=candidate_phone)
        
        experience_company = self.request.query_params.get('experience_company', None)
        if experience_company:
            queryset = queryset.filter(
                candidate__work_experiences__company_name__icontains=experience_company
            ).distinct()
        
        education_school = self.request.query_params.get('education_school', None)
        if education_school:
            queryset = queryset.filter(
                candidate__educations__school_name__icontains=education_school
            ).distinct()
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CandidateFlowListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CandidateFlowCreateSerializer
        return CandidateFlowSerializer
    
    def perform_create(self, serializer):
        candidate_flow = serializer.save(
            created_by=self.request.user,
            hr_company=self.request.user.hr_company
        )
        
        logger.info(f"Candidate flow created - Candidate: {candidate_flow.candidate.first_name} {candidate_flow.candidate.last_name} "
                   f"(Email: {candidate_flow.candidate.email}), "
                   f"Job: {candidate_flow.job_posting.title} (Code: {candidate_flow.job_posting.code}), "
                   f"Status: {candidate_flow.flow_status}, "
                   f"Created by: {self.request.user.username} (ID: {self.request.user.id})")
    
    @action(detail=False, methods=['get'])
    def my_flows(self, request):
        queryset = self.get_queryset().filter(created_by=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active_flows(self, request):
        queryset = self.get_queryset().filter(flow_status='active', is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.flow_status
        response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            logger.info(f"Candidate flow updated - Candidate: {instance.candidate.first_name} {instance.candidate.last_name}, "
                       f"Job: {instance.job_posting.title}, "
                       f"Status changed from '{old_status}' to '{instance.flow_status}', "
                       f"Updated by: {request.user.username} (ID: {request.user.id})")
        return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        flow_info = f"Candidate: {instance.candidate.first_name} {instance.candidate.last_name}, Job: {instance.job_posting.title}, ID: {instance.id}"
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            logger.warning(f"Candidate flow deleted - {flow_info}, "
                          f"Deleted by: {request.user.username} (ID: {request.user.id})")
        return response

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsHRUserPermission, HRCompanyPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['candidate_flow', 'activity_type', 'status', 'created_by', 'hr_company']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Activity.objects.all()
        
        return Activity.objects.filter(hr_company=user.hr_company)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ActivityCreateSerializer
        return ActivitySerializer
    
    def perform_create(self, serializer):
        activity = serializer.save(
            created_by=self.request.user,
            hr_company=self.request.user.hr_company
        )
        
        logger.info(f"Activity created - Type: {activity.activity_type.name}, "
                   f"Status: {activity.status.name}, "
                   f"Candidate Flow ID: {activity.candidate_flow.id}, "
                   f"Candidate: {activity.candidate_flow.candidate.first_name} {activity.candidate_flow.candidate.last_name}, "
                   f"Created by: {self.request.user.username} (ID: {self.request.user.id})")
    
    @action(detail=False, methods=['get'])
    def by_candidate_flow(self, request):
        candidate_flow_id = request.query_params.get('candidate_flow_id')
        if not candidate_flow_id:
            return Response({'error': 'candidate_flow_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        activities = self.get_queryset().filter(candidate_flow_id=candidate_flow_id)
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_activities(self, request):
        queryset = self.get_queryset().filter(created_by=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status.name if instance.status else 'None'
        response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            new_status = instance.status.name if instance.status else 'None'
            logger.info(f"Activity updated - Type: {instance.activity_type.name}, "
                       f"Status changed from '{old_status}' to '{new_status}', "
                       f"Candidate Flow ID: {instance.candidate_flow.id}, "
                       f"Updated by: {request.user.username} (ID: {request.user.id})")
        return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        activity_info = f"Type: {instance.activity_type.name}, Status: {instance.status.name if instance.status else 'None'}, ID: {instance.id}"
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            logger.warning(f"Activity deleted - {activity_info}, "
                          f"Deleted by: {request.user.username} (ID: {request.user.id})")
        return response

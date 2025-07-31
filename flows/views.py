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
            return CandidateFlow.objects.all()
        
        return CandidateFlow.objects.filter(
            hr_company=user.hr_company,
            job_posting__customer_company__in=user.get_authorized_customer_companies()
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CandidateFlowListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CandidateFlowCreateSerializer
        return CandidateFlowSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            hr_company=self.request.user.hr_company
        )
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
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
        serializer.save(
            created_by=self.request.user,
            hr_company=self.request.user.hr_company
        )
    
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

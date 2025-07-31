from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Candidate, Education, WorkExperience
from .serializers import (
    CandidateSerializer, CandidateCreateSerializer,
    EducationSerializer, WorkExperienceSerializer
)
from common.permissions import IsHRUserPermission, CandidateAccessPermission

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsHRUserPermission, CandidateAccessPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Candidate.objects.all()
        
        user_authorized_companies = user.get_authorized_customer_companies()
        
        queryset = Candidate.objects.filter(
            candidate_flows__hr_company=user.hr_company,
            candidate_flows__job_posting__customer_company__in=user_authorized_companies
        ).distinct()
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        company = self.request.query_params.get('company', None)
        if company:
            queryset = queryset.filter(
                work_experiences__company_name__icontains=company
            ).distinct()
        
        school = self.request.query_params.get('school', None)
        if school:
            queryset = queryset.filter(
                educations__school_name__icontains=school
            ).distinct()
        
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CandidateCreateSerializer
        return CandidateSerializer
    
    
    @action(detail=False, methods=['get'])
    def search_by_experience(self, request):
        company = request.query_params.get('company', '')
        if not company:
            return Response({'error': 'Company parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        candidates = Candidate.objects.filter(
            work_experiences__company_name__icontains=company
        ).distinct()
        
        serializer = self.get_serializer(candidates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search_by_education(self, request):
        school = request.query_params.get('school', '')
        if not school:
            return Response({'error': 'School parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        candidates = Candidate.objects.filter(
            educations__school_name__icontains=school
        ).distinct()
        
        serializer = self.get_serializer(candidates, many=True)
        return Response(serializer.data)

class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [IsHRUserPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['candidate', 'is_current']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Education.objects.all()
        
        user_authorized_companies = user.get_authorized_customer_companies()
        
        return Education.objects.filter(
            candidate__candidate_flows__hr_company=user.hr_company,
            candidate__candidate_flows__job_posting__customer_company__in=user_authorized_companies
        ).distinct()

class WorkExperienceViewSet(viewsets.ModelViewSet):
    queryset = WorkExperience.objects.all()
    serializer_class = WorkExperienceSerializer
    permission_classes = [IsHRUserPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['candidate', 'is_current']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return WorkExperience.objects.all()
        
        user_authorized_companies = user.get_authorized_customer_companies()
        
        return WorkExperience.objects.filter(
            candidate__candidate_flows__hr_company=user.hr_company,
            candidate__candidate_flows__job_posting__customer_company__in=user_authorized_companies
        ).distinct()

from rest_framework import serializers
from .models import ActivityType, Status, CandidateFlow, Activity
from jobs.serializers import JobPostingSerializer
from candidates.serializers import CandidateSerializer
from accounts.serializers import HRUserSerializer
from companies.serializers import HRCompanySerializer

class ActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityType
        fields = ['id', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class StatusSerializer(serializers.ModelSerializer):
    activity_type_detail = ActivityTypeSerializer(source='activity_type', read_only=True)
    
    class Meta:
        model = Status
        fields = [
            'id', 'name', 'activity_type', 'description', 'is_active', 'created_at',
            'activity_type_detail'
        ]
        read_only_fields = ['id', 'created_at']

class ActivitySerializer(serializers.ModelSerializer):
    activity_type_detail = ActivityTypeSerializer(source='activity_type', read_only=True)
    status_detail = StatusSerializer(source='status', read_only=True)
    created_by_detail = HRUserSerializer(source='created_by', read_only=True)
    hr_company_detail = HRCompanySerializer(source='hr_company', read_only=True)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'candidate_flow', 'activity_type', 'status', 'created_by',
            'hr_company', 'notes', 'created_at', 'updated_at',
            'activity_type_detail', 'status_detail', 'created_by_detail', 'hr_company_detail'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'hr_company']

class ActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['candidate_flow', 'activity_type', 'status', 'notes']
    
    def validate(self, data):
        activity_type = data.get('activity_type')
        status = data.get('status')
        if status.activity_type != activity_type:
            raise serializers.ValidationError(
                "Selected status does not belong to the selected activity type."
            )
        
        return data

class CandidateFlowSerializer(serializers.ModelSerializer):
    job_posting_detail = JobPostingSerializer(source='job_posting', read_only=True)
    candidate_detail = CandidateSerializer(source='candidate', read_only=True)
    hr_company_detail = HRCompanySerializer(source='hr_company', read_only=True)
    created_by_detail = HRUserSerializer(source='created_by', read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)
    
    class Meta:
        model = CandidateFlow
        fields = [
            'id', 'job_posting', 'candidate', 'hr_company', 'created_by',
            'flow_status', 'notes', 'is_active', 'created_at', 'updated_at',
            'job_posting_detail', 'candidate_detail', 'hr_company_detail',
            'created_by_detail', 'activities'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'hr_company']

class CandidateFlowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateFlow
        fields = ['job_posting', 'candidate', 'flow_status', 'notes']
    
    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            job_posting = data.get('job_posting')
            
            if not user.has_customer_company_permission(job_posting.customer_company):
                raise serializers.ValidationError(
                    "You don't have permission to create candidate flows for this job posting."
                )
        
        return data

class CandidateFlowListSerializer(serializers.ModelSerializer):
    job_posting_title = serializers.CharField(source='job_posting.title', read_only=True)
    job_posting_code = serializers.CharField(source='job_posting.code', read_only=True)
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    candidate_email = serializers.CharField(source='candidate.email', read_only=True)
    candidate_phone = serializers.CharField(source='candidate.phone', read_only=True)
    hr_company_name = serializers.CharField(source='hr_company.name', read_only=True)
    
    class Meta:
        model = CandidateFlow
        fields = [
            'id', 'flow_status', 'created_at', 'updated_at',
            'job_posting_title', 'job_posting_code', 'candidate_name',
            'candidate_email', 'candidate_phone', 'hr_company_name'
        ]
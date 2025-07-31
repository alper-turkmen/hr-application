from rest_framework import serializers
from .models import JobPosting
from companies.serializers import HRCompanySerializer, CustomerCompanySerializer
from accounts.serializers import HRUserSerializer

class JobPostingSerializer(serializers.ModelSerializer):
    hr_company_detail = HRCompanySerializer(source='hr_company', read_only=True)
    customer_company_detail = CustomerCompanySerializer(source='customer_company', read_only=True)
    created_by_detail = HRUserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'code', 'description', 'hr_company', 'customer_company',
            'created_by', 'closing_date', 'status', 'is_active', 'created_at', 'updated_at',
            'hr_company_detail', 'customer_company_detail', 'created_by_detail'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class JobPostingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = [
            'title', 'code', 'description', 'customer_company',
            'closing_date', 'status', 'created_by', 'hr_company'
        ]
        read_only_fields = ['created_by', 'hr_company']
        
    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            customer_company = data.get('customer_company')
            
            if not user.has_customer_company_permission(customer_company):
                raise serializers.ValidationError(
                    "You don't have permission to create job postings for this customer company."
                )
        
        return data
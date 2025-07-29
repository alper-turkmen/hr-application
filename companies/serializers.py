from rest_framework import serializers
from .models import HRCompany, CustomerCompany

class HRCompanySerializer(serializers.ModelSerializer):
    hr_users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = HRCompany
        fields = [
            'id', 
            'name', 
            'code', 
            'is_active', 
            'created_at', 
            'updated_at',
            'hr_users_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_hr_users_count(self, obj):
        return obj.hr_users.filter(is_active=True).count()

class CustomerCompanySerializer(serializers.ModelSerializer):
    authorized_hr_users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerCompany
        fields = [
            'id',
            'name', 
            'code', 
            'is_active', 
            'created_at', 
            'updated_at',
            'authorized_hr_users_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_authorized_hr_users_count(self, obj):
        return obj.authorized_hr_users.filter(is_active=True).count()

class HRCompanySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HRCompany
        fields = ['id', 'name', 'code']

class CustomerCompanySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCompany
        fields = ['id', 'name', 'code']
from rest_framework import serializers
from .models import Candidate, Education, WorkExperience

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            'id', 'school_name', 'department', 'degree', 'start_date', 'end_date',
            'is_current', 'gpa', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = [
            'id', 'company_name', 'position', 'description', 'start_date', 'end_date',
            'is_current', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class CandidateSerializer(serializers.ModelSerializer):
    educations = EducationSerializer(many=True, read_only=True)
    work_experiences = WorkExperienceSerializer(many=True, read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Candidate
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'address',
            'is_active', 'created_at', 'updated_at', 'full_name',
            'educations', 'work_experiences'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name']

class CandidateCreateSerializer(serializers.ModelSerializer):
    educations = EducationSerializer(many=True, required=False)
    work_experiences = WorkExperienceSerializer(many=True, required=False)
    
    class Meta:
        model = Candidate
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address',
            'educations', 'work_experiences'
        ]
    
    def create(self, validated_data):
        educations_data = validated_data.pop('educations', [])
        work_experiences_data = validated_data.pop('work_experiences', [])
        
        candidate = Candidate.objects.create(**validated_data)
        
        for education_data in educations_data:
            Education.objects.create(candidate=candidate, **education_data)
        
        for work_experience_data in work_experiences_data:
            WorkExperience.objects.create(candidate=candidate, **work_experience_data)
        
        return candidate
    
    def update(self, instance, validated_data):
        educations_data = validated_data.pop('educations', [])
        work_experiences_data = validated_data.pop('work_experiences', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if educations_data:
            instance.educations.all().delete()
            for education_data in educations_data:
                Education.objects.create(candidate=instance, **education_data)
        
        if work_experiences_data:
            instance.work_experiences.all().delete()
            for work_experience_data in work_experiences_data:
                WorkExperience.objects.create(candidate=instance, **work_experience_data)
        
        return instance
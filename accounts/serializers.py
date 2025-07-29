from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import HRUser
from companies.serializers import HRCompanySimpleSerializer, CustomerCompanySimpleSerializer

class HRUserSerializer(serializers.ModelSerializer):
    hr_company_detail = HRCompanySimpleSerializer(source='hr_company', read_only=True)
    authorized_customer_companies_detail = CustomerCompanySimpleSerializer(
        source='authorized_customer_companies', 
        many=True, 
        read_only=True
    )
    authorized_companies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = HRUser
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'is_active',
            'is_staff',
            'is_superuser',
            'hr_company',
            'hr_company_detail',
            'authorized_customer_companies',
            'authorized_customer_companies_detail',
            'authorized_companies_count',
            'created_at',
            'updated_at',
            'last_login',
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_authorized_companies_count(self, obj):
        return obj.authorized_customer_companies.filter(is_active=True).count()

class HRUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = HRUser
        fields = [
            'username',
            'email', 
            'first_name',
            'last_name',
            'phone',
            'password',
            'password_confirm',
            'hr_company',
            'authorized_customer_companies',
            'is_active'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Şifreler eşleşmiyor!")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        authorized_companies = validated_data.pop('authorized_customer_companies', [])
        
        user = HRUser.objects.create_user(password=password, **validated_data)
        user.authorized_customer_companies.set(authorized_companies)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Kullanıcı adı veya şifre hatalı!')
            if not user.is_active:
                raise serializers.ValidationError('Hesap deaktif!')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Kullanıcı adı ve şifre gerekli!')
        
        return attrs

class HRUserProfileSerializer(serializers.ModelSerializer):
    hr_company_name = serializers.CharField(source='hr_company.name', read_only=True)
    authorized_companies_list = serializers.StringRelatedField(
        source='authorized_customer_companies', 
        many=True, 
        read_only=True
    )
    
    class Meta:
        model = HRUser
        fields = [
            'id',
            'username',
            'email',
            'first_name', 
            'last_name',
            'phone',
            'hr_company_name',
            'authorized_companies_list',
        ]
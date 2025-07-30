import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from companies.models import HRCompany, CustomerCompany
from .models import HRUser
from .serializers import (
    HRUserSerializer,
    HRUserCreateSerializer,
    LoginSerializer,
    HRUserProfileSerializer
)

User = get_user_model()


class HRUserModelTest(TestCase):
    def setUp(self):
        self.hr_company = HRCompany.objects.create(
            name="Test HR Company",
            code="THR001"
        )
        self.customer_company1 = CustomerCompany.objects.create(
            name="Customer Company 1",
            code="CC001"
        )
        self.customer_company2 = CustomerCompany.objects.create(
            name="Customer Company 2",
            code="CC002",
            is_active=False
        )
        
    def test_create_hr_user(self):
        user = HRUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            hr_company=self.hr_company
        )
        
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.hr_company, self.hr_company)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        
    def test_create_superuser(self):
        user = HRUser.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        
    def test_user_str_representation(self):
        user = HRUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            hr_company=self.hr_company
        )
        
        expected_str = f"testuser - {self.hr_company.name}"
        self.assertEqual(str(user), expected_str)
        
    def test_user_str_representation_without_company(self):
        user = HRUser.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )
        
        expected_str = "admin - Admin"
        self.assertEqual(str(user), expected_str)
        
    def test_get_authorized_customer_companies(self):
        user = HRUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        user.authorized_customer_companies.add(
            self.customer_company1, 
            self.customer_company2
        )
        
        authorized_companies = user.get_authorized_customer_companies()
        
        self.assertEqual(authorized_companies.count(), 1)
        self.assertIn(self.customer_company1, authorized_companies)
        self.assertNotIn(self.customer_company2, authorized_companies)
        
    def test_has_customer_company_permission(self):
        user = HRUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        user.authorized_customer_companies.add(self.customer_company1)
        
        self.assertTrue(user.has_customer_company_permission(self.customer_company1))
        self.assertFalse(user.has_customer_company_permission(self.customer_company2))
        
    def test_is_hr_staff_property(self):
        hr_user = HRUser.objects.create_user(
            username="hruser",
            email="hr@example.com",
            password="testpass123",
            hr_company=self.hr_company
        )
        
        superuser = HRUser.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )
        
        regular_user = HRUser.objects.create_user(
            username="regular",
            email="regular@example.com",
            password="testpass123"
        )
        
        self.assertTrue(hr_user.is_hr_staff)
        self.assertFalse(superuser.is_hr_staff)
        self.assertFalse(regular_user.is_hr_staff)


class HRUserSerializerTest(TestCase):
    def setUp(self):
        self.hr_company = HRCompany.objects.create(
            name="Test HR Company",
            code="THR001"
        )
        self.customer_company = CustomerCompany.objects.create(
            name="Customer Company",
            code="CC001"
        )
        
    def test_hr_user_serializer(self):
        user = HRUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            hr_company=self.hr_company,
            first_name="Test",
            last_name="User"
        )
        user.authorized_customer_companies.add(self.customer_company)
        
        serializer = HRUserSerializer(user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['last_name'], 'User')
        self.assertEqual(data['authorized_companies_count'], 1)
        self.assertIn('hr_company_detail', data)
        self.assertIn('authorized_customer_companies_detail', data)
        
    def test_hr_user_create_serializer_valid(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'hr_company': self.hr_company.id,
            'authorized_customer_companies': [self.customer_company.id]
        }
        
        serializer = HRUserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.hr_company, self.hr_company)
        self.assertTrue(user.check_password('newpass123'))
        self.assertIn(self.customer_company, user.authorized_customer_companies.all())
        
    def test_hr_user_create_serializer_password_mismatch(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'differentpass',
            'hr_company': self.hr_company.id
        }
        
        serializer = HRUserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        
    def test_login_serializer_valid(self):
        user = HRUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], user)
        
    def test_login_serializer_invalid_credentials(self):
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        
    def test_login_serializer_inactive_user(self):
        user = HRUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_active=False
        )
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        
    def test_hr_user_profile_serializer(self):
        user = HRUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            hr_company=self.hr_company,
            first_name="Test",
            last_name="User"
        )
        user.authorized_customer_companies.add(self.customer_company)
        
        serializer = HRUserProfileSerializer(user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['hr_company_name'], self.hr_company.name)
        self.assertIn('authorized_companies_list', data)


class AuthViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.hr_company = HRCompany.objects.create(
            name="Test HR Company",
            code="THR001"
        )
        self.user = HRUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            hr_company=self.hr_company
        )
        
    def test_login_success(self):
        url = reverse('auth-login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['message'], 'Login successful!')
        
    def test_login_invalid_credentials(self):
        url = reverse('auth-login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('auth-profile')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
        
    def test_profile_unauthenticated(self):
        url = reverse('auth-profile')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_session_login_success(self):
        url = reverse('auth-session-login')
        data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Login successful!')
        self.assertIn('user', response.data)
        

class HRUserViewSetTest(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        
        self.hr_company1 = HRCompany.objects.create(
            name="HR Company 1",
            code="HR001"
        )
        self.hr_company2 = HRCompany.objects.create(
            name="HR Company 2", 
            code="HR002"
        )
        
        self.customer_company = CustomerCompany.objects.create(
            name="Customer Company",
            code="CC001"
        )
        
        self.superuser = HRUser.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )
        
        self.hr_user1 = HRUser.objects.create_user(
            username="hruser1",
            email="hr1@example.com",
            password="hrpass123",
            hr_company=self.hr_company1
        )
        
        self.hr_user2 = HRUser.objects.create_user(
            username="hruser2",
            email="hr2@example.com",
            password="hrpass123",
            hr_company=self.hr_company2
        )
        
    def test_list_users_as_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('hruser-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)  
        
    def test_list_users_as_hr_user(self):
        self.client.force_authenticate(user=self.hr_user1)
        url = reverse('hruser-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1) 
        
    def test_list_users_unauthenticated(self):
        url = reverse('hruser-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_create_user_as_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('hruser-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'hr_company': self.hr_company1.id,
            'authorized_customer_companies': [self.customer_company.id]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertEqual(response.data['email'], 'newuser@example.com')
        
        user = HRUser.objects.get(username='newuser')
        self.assertEqual(user.hr_company, self.hr_company1)
        self.assertIn(self.customer_company, user.authorized_customer_companies.all())
        
    def test_retrieve_user(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('hruser-detail', kwargs={'pk': self.hr_user1.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.hr_user1.username)
        
    def test_update_user(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('hruser-detail', kwargs={'pk': self.hr_user1.pk})
        data = {
            'username': self.hr_user1.username,
            'email': self.hr_user1.email,
            'first_name': 'Updated',
            'last_name': 'Name',
            'hr_company': self.hr_company1.id
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
        
    def test_partial_update_user(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('hruser-detail', kwargs={'pk': self.hr_user1.pk})
        data = {
            'first_name': 'Partially Updated'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Partially Updated')
        
    def test_delete_user(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('hruser-detail', kwargs={'pk': self.hr_user1.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(HRUser.objects.filter(pk=self.hr_user1.pk).exists())
        

    def test_search_users(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('hruser-list')
        
        response = self.client.get(url, {'search': 'hruser1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        response = self.client.get(url, {'search': 'hr1@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
    def test_filter_users(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('hruser-list')
        
        response = self.client.get(url, {'hr_company': self.hr_company1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        response = self.client.get(url, {'is_active': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        
    def test_ordering_users(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('hruser-list')
        
        response = self.client.get(url, {'ordering': 'username'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PermissionTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.hr_company1 = HRCompany.objects.create(
            name="HR Company 1",
            code="HR001"
        )
        self.hr_company2 = HRCompany.objects.create(
            name="HR Company 2",
            code="HR002"
        )
        
        self.customer_company1 = CustomerCompany.objects.create(
            name="Customer Company 1",
            code="CC001"
        )
        self.customer_company2 = CustomerCompany.objects.create(
            name="Customer Company 2",
            code="CC002"
        )
        
        self.superuser = HRUser.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )
        
        self.hr_user1 = HRUser.objects.create_user(
            username="hruser1",
            email="hr1@example.com",
            password="hrpass123",
            hr_company=self.hr_company1
        )
        self.hr_user1.authorized_customer_companies.add(self.customer_company1)
        
        self.hr_user2 = HRUser.objects.create_user(
            username="hruser2",
            email="hr2@example.com",
            password="hrpass123",
            hr_company=self.hr_company2
        )
        self.hr_user2.authorized_customer_companies.add(self.customer_company2)
        
    def test_hr_user_can_only_see_same_company_users(self):
        self.client.force_authenticate(user=self.hr_user1)
        url = reverse('hruser-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        returned_user = response.data['results'][0]
        self.assertEqual(returned_user['username'], self.hr_user1.username)
        
    def test_hr_user_cannot_access_other_company_user(self):
        self.client.force_authenticate(user=self.hr_user1)
        url = reverse('hruser-detail', kwargs={'pk': self.hr_user2.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_superuser_can_see_all_users(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('hruser-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3) 
        
    def test_customer_company_permission_check(self):
        self.assertTrue(
            self.hr_user1.has_customer_company_permission(self.customer_company1)
        )
        
        self.assertFalse(
            self.hr_user1.has_customer_company_permission(self.customer_company2)
        )
        
    def test_get_authorized_customer_companies_only_active(self):
        self.customer_company1.is_active = False
        self.customer_company1.save()
        
        authorized_companies = self.hr_user1.get_authorized_customer_companies()
        
        self.assertEqual(authorized_companies.count(), 0)


class AuthenticationFlowTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.hr_company = HRCompany.objects.create(
            name="Test HR Company",
            code="THR001"
        )
        self.user = HRUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            hr_company=self.hr_company,
            first_name="Test",
            last_name="User"
        )
        
    def test_complete_authentication_flow(self):
        login_url = reverse('auth-login')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        login_response = self.client.post(login_url, login_data, format='json')
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)
        
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_url = reverse('auth-profile')
        
        profile_response = self.client.get(profile_url)
        
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['username'], self.user.username)
        
        self.client.credentials()  
        
        profile_response_unauth = self.client.get(profile_url)
        
        self.assertEqual(profile_response_unauth.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_jwt_token_authentication(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('hruser-me')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        
    def test_invalid_jwt_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        url = reverse('auth-profile')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUtilities:
    @staticmethod
    def create_test_hr_company(name="Test HR Company", code="THR001"):
        return HRCompany.objects.create(name=name, code=code)
    
    @staticmethod
    def create_test_customer_company(name="Test Customer Company", code="CC001", is_active=True):
        return CustomerCompany.objects.create(name=name, code=code, is_active=is_active)
    
    @staticmethod
    def create_test_hr_user(username="testuser", email="test@example.com", password="testpass123", hr_company=None):
        return HRUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            hr_company=hr_company
        )
    
    @staticmethod
    def create_test_superuser(username="admin", email="admin@example.com", password="adminpass123"):
        return HRUser.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

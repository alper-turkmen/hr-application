# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser
from companies.models import HRCompany, CustomerCompany

class HRUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    email = models.EmailField(unique=True)

    hr_company = models.ForeignKey(
        HRCompany, 
        on_delete=models.CASCADE,
        related_name='hr_users',
        null=True,
        blank=True 
    )
    
    authorized_customer_companies = models.ManyToManyField(
        CustomerCompany,
        related_name='authorized_hr_users',
        blank=True
    )
    
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.hr_company:
            return f"{self.username} - {self.hr_company.name}"
        return f"{self.username} - Admin"
    
    def get_authorized_customer_companies(self):
        return self.authorized_customer_companies.filter(is_active=True)
    
    def has_customer_company_permission(self, customer_company):
        return self.authorized_customer_companies.filter(
            id=customer_company.id, 
            is_active=True
        ).exists()
    
    @property
    def is_hr_staff(self):
        return bool(self.hr_company and not self.is_superuser)
    
    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['hr_company']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['hr_company', 'is_active']), 
            models.Index(fields=['-created_at']),
        ]
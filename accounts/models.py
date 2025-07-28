from django.db import models
from django.contrib.auth.models import AbstractUser
from companies.models import HRCompany, CustomerCompany

# Create your models here.

class HRUser(AbstractUser):
    hr_company = models.ForeignKey(
        HRCompany, 
        on_delete=models.CASCADE, 
        related_name='hr_users'
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
        return f"{self.username} - {self.hr_company.name}"

    def get_authorized_customer_companies(self):
        return self.authorized_customer_companies.filter(is_active=True)

    def has_customer_company_permission(self, customer_company):
        return self.authorized_customer_companies.filter(
            id=customer_company.id, 
            is_active=True
        ).exists()
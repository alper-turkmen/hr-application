from django.db import models
from companies.models import HRCompany, CustomerCompany
from accounts.models import HRUser

class JobPosting(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    hr_company = models.ForeignKey(
        HRCompany,
        on_delete=models.CASCADE,
        related_name='job_postings'
    )
    customer_company = models.ForeignKey(
        CustomerCompany,
        on_delete=models.CASCADE,
        related_name='job_postings'
    )
    created_by = models.ForeignKey(
        HRUser,
        on_delete=models.CASCADE,
        related_name='created_job_postings'
    )
    closing_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    class Meta:
        ordering = ['-created_at']

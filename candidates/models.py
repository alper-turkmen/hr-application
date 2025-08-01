from django.db import models

class Candidate(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['first_name']),
            models.Index(fields=['last_name']),
            models.Index(fields=['phone']),
            models.Index(fields=['first_name', 'last_name']), 
            models.Index(fields=['-created_at']), 
        ]

class Education(models.Model):
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='educations'
    )
    school_name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    degree = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.candidate.full_name} - {self.school_name}"
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['candidate']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['is_current']),
            models.Index(fields=['school_name']),
            models.Index(fields=['candidate', 'start_date']), 
            models.Index(fields=['-start_date']), 
        ]

class WorkExperience(models.Model):
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='work_experiences'
    )
    company_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.candidate.full_name} - {self.company_name}"
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['candidate']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['is_current']),
            models.Index(fields=['company_name']),
            models.Index(fields=['candidate', 'start_date']), 
            models.Index(fields=['-start_date']), 
        ]

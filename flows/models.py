from django.db import models
from jobs.models import JobPosting
from candidates.models import Candidate
from accounts.models import HRUser
from companies.models import HRCompany

class ActivityType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=100)
    activity_type = models.ForeignKey(
        ActivityType,
        on_delete=models.CASCADE,
        related_name='statuses'
    )
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.activity_type.name} - {self.name}"
    
    class Meta:
        unique_together = ['name', 'activity_type']

class CandidateFlow(models.Model):
    FLOW_STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('on_hold', 'On Hold'),
    ]
    
    job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='candidate_flows'
    )
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='candidate_flows'
    )
    hr_company = models.ForeignKey(
        HRCompany,
        on_delete=models.CASCADE,
        related_name='candidate_flows'
    )
    created_by = models.ForeignKey(
        HRUser,
        on_delete=models.CASCADE,
        related_name='created_candidate_flows'
    )
    flow_status = models.CharField(max_length=20, choices=FLOW_STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.candidate.full_name} - {self.job_posting.title}"
    
    class Meta:
        unique_together = ['job_posting', 'candidate']
        ordering = ['-created_at']

class Activity(models.Model):
    candidate_flow = models.ForeignKey(
        CandidateFlow,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.ForeignKey(
        ActivityType,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    created_by = models.ForeignKey(
        HRUser,
        on_delete=models.CASCADE,
        related_name='created_activities'
    )
    hr_company = models.ForeignKey(
        HRCompany,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.candidate_flow} - {self.activity_type.name}"
    
    class Meta:
        ordering = ['-created_at']

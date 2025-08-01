from django.db import models
from django.utils.translation import gettext_lazy as _


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('weekly_activity', _('Weekly Activity Report')),
        ('monthly_activity', _('Monthly Activity Report')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('generating', _('Generating')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]
    
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_path = models.CharField(max_length=500, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    generated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-generated_at']
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['generated_at']),
            models.Index(fields=['completed_at']),
            models.Index(fields=['report_type', 'status']), 
            models.Index(fields=['start_date', 'end_date']), 
            models.Index(fields=['-generated_at']), 
        ]
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.start_date} to {self.end_date}"

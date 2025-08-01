from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'report_type',
        'status',
        'start_date',
        'end_date',
        'generated_at',
        'completed_at'
    ]
    list_filter = [
        'report_type',
        'status',
        'generated_at'
    ]
    search_fields = [
        'report_type',
        'file_path'
    ]
    readonly_fields = [
        'generated_at',
        'completed_at'
    ]
    ordering = ['-generated_at']
    
    def has_add_permission(self, request):
        return False

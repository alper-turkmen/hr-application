from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id',
            'report_type',
            'report_type_display',
            'status',
            'status_display',
            'file_path',
            'start_date',
            'end_date',
            'generated_at',
            'completed_at',
            'error_message'
        ]
        read_only_fields = [
            'id',
            'report_type_display',
            'status_display',
            'file_path',
            'generated_at',
            'completed_at',
            'error_message'
        ]


class ReportCreateSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=Report.REPORT_TYPE_CHOICES)
    
    def validate_report_type(self, value):
        if value not in ['weekly_activity', 'monthly_activity']:
            raise serializers.ValidationError("Unsupported report type")
        return value
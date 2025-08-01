import os
import logging
from django.http import FileResponse, Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsHRUserPermission
from .models import Report
from .serializers import ReportSerializer, ReportCreateSerializer

try:
    from .tasks import generate_weekly_activity_report, generate_monthly_activity_report
    CELERY_AVAILABLE = True
except Exception as e:
    CELERY_AVAILABLE = False
    logging.warning(f"Celery not available: {e}")

logger = logging.getLogger('wisehire.reports')


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, IsHRUserPermission]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'hr_company'):
            return Report.objects.all()
        return Report.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportCreateSerializer
        return ReportSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        report_type = serializer.validated_data['report_type']
        
        try:
            if not CELERY_AVAILABLE:
                return Response(
                    {'error': _('Report generation service is not available')},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            if report_type == 'weekly_activity':
                task = generate_weekly_activity_report.delay()
                message = _("Weekly activity report generation started")
            elif report_type == 'monthly_activity':
                task = generate_monthly_activity_report.delay()
                message = _("Monthly activity report generation started")
            else:
                return Response(
                    {'error': _('Unsupported report type')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Report generation task started: {task.id} for type: {report_type}")
            
            return Response({
                'message': message,
                'task_id': task.id,
                'report_type': report_type
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            logger.error(f"Error starting report generation: {str(e)}")
            return Response(
                {'error': _('Failed to start report generation')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        try:
            report = self.get_object()
            
            if report.status != 'completed':
                return Response(
                    {'error': _('Report is not ready for download')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not report.file_path or not os.path.exists(report.file_path):
                return Response(
                    {'error': _('Report file not found')},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            filename = os.path.basename(report.file_path)
            response = FileResponse(
                open(report.file_path, 'rb'),
                as_attachment=True,
                filename=filename
            )
            
            logger.info(f"Report downloaded: {report.id} by user: {request.user.id}")
            return response
            
        except Report.DoesNotExist:
            raise Http404(_("Report not found"))
        except Exception as e:
            logger.error(f"Error downloading report: {str(e)}")
            return Response(
                {'error': _('Failed to download report')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_weekly_report(self, request):
        try:
            if not CELERY_AVAILABLE:
                return Response(
                    {'error': _('Report generation service is not available')},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            task = generate_weekly_activity_report.delay()
            logger.info(f"Weekly report generation task started: {task.id}")
            
            return Response({
                'message': _("Weekly activity report generation started"),
                'task_id': task.id
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            logger.error(f"Error starting weekly report generation: {str(e)}")
            return Response(
                {'error': _('Failed to start weekly report generation')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_monthly_report(self, request):
        try:
            if not CELERY_AVAILABLE:
                return Response(
                    {'error': _('Report generation service is not available')},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            task = generate_monthly_activity_report.delay()
            logger.info(f"Monthly report generation task started: {task.id}")
            
            return Response({
                'message': _("Monthly activity report generation started"),
                'task_id': task.id
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            logger.error(f"Error starting monthly report generation: {str(e)}")
            return Response(
                {'error': _('Failed to start monthly report generation')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

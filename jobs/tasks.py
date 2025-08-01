import logging
from datetime import datetime
from django.utils import timezone
from celery import shared_task
from .models import JobPosting

logger = logging.getLogger('wisehire.jobs')


@shared_task
def close_expired_jobs():
    logger.info("Starting expired jobs closure task")
    
    try:
        now = timezone.now()
        expired_jobs = JobPosting.objects.filter(
            closing_date__lt=now,
            status='active'
        )
        
        count = expired_jobs.count()
        if count > 0:
            expired_jobs.update(status='inactive')
            logger.info(f"Closed {count} expired job postings")
            return f"Closed {count} expired job postings"
        else:
            logger.info("No expired job postings found")
            return "No expired job postings found"
            
    except Exception as e:
        logger.error(f"Error closing expired jobs: {str(e)}")
        return f"Error: {str(e)}"
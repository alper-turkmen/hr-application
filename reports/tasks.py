import os
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Count
from django.utils import timezone
from celery import shared_task
from flows.models import Activity, ActivityType
from .models import Report

logger = logging.getLogger('wisehire.reports')


def generate_latex_report(title, data, report_type, start_date, end_date):
    latex_content = f"""
\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{booktabs}}
\\usepackage{{geometry}}
\\geometry{{a4paper, margin=1in}}
\\usepackage{{fancyhdr}}
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\rhead{{\\today}}
\\lhead{{{title}}}
\\cfoot{{\\thepage}}

\\title{{{title}}}
\\author{{WiseHire Reports}}
\\date{{\\today}}

\\begin{{document}}
\\maketitle

\\section{{Report Period}}
From: {start_date.strftime('%Y-%m-%d')} \\\\
To: {end_date.strftime('%Y-%m-%d')}

\\section{{Data}}
\\begin{{table}}[h!]
\\centering
\\begin{{tabular}}{{|l|c|}}
\\hline
\\textbf{{Activity Type}} & \\textbf{{Count}} \\\\
\\hline
"""
    
    for item in data:
        activity_name = item['activity_type__name'] or 'Unknown'
        count = item['count']
        latex_content += f"{activity_name} & {count} \\\\\n\\hline\n"
    
    latex_content += """
\\end{tabular}
\\caption{Activity Statistics}
\\end{table}


\\end{document}
"""
    
    return latex_content


def compile_latex_to_pdf(latex_content, output_path):
    import subprocess
    import tempfile
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, 'report.tex')
            
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            result = subprocess.run([
                'pdflatex', '-interaction=nonstopmode', '-output-directory', temp_dir, tex_file
            ], capture_output=True, text=True, cwd=temp_dir)
            
            if result.returncode == 0:
                pdf_file = os.path.join(temp_dir, 'report.pdf')
                if os.path.exists(pdf_file):
                    import shutil
                    shutil.copy2(pdf_file, output_path)
                    return True
                else:
                    logger.error(f"PDF file not found after compilation: {pdf_file}")
                    return False
            else:
                logger.error(f"LaTeX compilation failed: {result.stderr}")
                return False
                
    except Exception as e:
        logger.error(f"Error compiling LaTeX: {str(e)}")
        return False


@shared_task
def generate_weekly_activity_report():
  
    logger.info("Starting weekly activity report generation")
    
    try:
        now = timezone.now()
        start_of_year = datetime(now.year, 1, 1, tzinfo=now.tzinfo)
        
        report = Report.objects.create(
            report_type='weekly_activity',
            status='generating',
            start_date=start_of_year.date(),
            end_date=now.date()
        )
        
        activities = Activity.objects.filter(
            created_at__gte=start_of_year,
            created_at__lte=now
        ).values('activity_type__name').annotate(
            count=Count('id')
        ).order_by('activity_type__name')
        
        filename = f"weekly_activity_report_{now.strftime('%Y_%m_%d')}.pdf"
        reports_dir = os.path.join(settings.BASE_DIR, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        output_path = os.path.join(reports_dir, filename)
        
        title = f"Weekly Activity Report - {now.year}"
        latex_content = generate_latex_report(
            title, activities, 'weekly_activity', 
            start_of_year.date(), now.date()
        )
        
        if compile_latex_to_pdf(latex_content, output_path):
            report.status = 'completed'
            report.file_path = output_path
            report.completed_at = timezone.now()
            report.save()
            
            logger.info(f"Weekly activity report generated successfully: {output_path}")
            return f"Weekly activity report generated: {filename}"
        else:
            report.status = 'failed'
            report.error_message = "Failed to compile LaTeX to PDF"
            report.save()
            
            logger.error("Failed to compile weekly activity report")
            return "Failed to generate weekly activity report"
            
    except Exception as e:
        logger.error(f"Error generating weekly activity report: {str(e)}")
        if 'report' in locals():
            report.status = 'failed'
            report.error_message = str(e)
            report.save()
        return f"Error: {str(e)}"


@shared_task
def generate_monthly_activity_report():
    logger.info("Starting monthly activity report generation")
    
    try:
        now = timezone.now()
        start_of_year = datetime(now.year, 1, 1, tzinfo=now.tzinfo)
        
        report = Report.objects.create(
            report_type='monthly_activity',
            status='generating',
            start_date=start_of_year.date(),
            end_date=now.date()
        )
        
        activities = Activity.objects.filter(
            created_at__gte=start_of_year,
            created_at__lte=now
        ).values('activity_type__name').annotate(
            count=Count('id')
        ).order_by('activity_type__name')
        
        filename = f"monthly_activity_report_{now.strftime('%Y_%m_%d')}.pdf"
        reports_dir = os.path.join(settings.BASE_DIR, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        output_path = os.path.join(reports_dir, filename)
        
        title = f"Monthly Activity Report - {now.year}"
        latex_content = generate_latex_report(
            title, activities, 'monthly_activity', 
            start_of_year.date(), now.date()
        )
        
        if compile_latex_to_pdf(latex_content, output_path):
            report.status = 'completed'
            report.file_path = output_path
            report.completed_at = timezone.now()
            report.save()
            
            logger.info(f"Monthly activity report generated successfully: {output_path}")
            return f"Monthly activity report generated: {filename}"
        else:
            report.status = 'failed'
            report.error_message = "Failed to compile LaTeX to PDF"
            report.save()
            
            logger.error("Failed to compile monthly activity report")
            return "Failed to generate monthly activity report"
            
    except Exception as e:
        logger.error(f"Error generating monthly activity report: {str(e)}")
        if 'report' in locals():
            report.status = 'failed'
            report.error_message = str(e)
            report.save()
        return f"Error: {str(e)}"
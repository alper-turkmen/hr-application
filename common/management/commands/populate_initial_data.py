from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from companies.models import HRCompany, CustomerCompany
from accounts.models import HRUser
from candidates.models import Candidate, Education, WorkExperience
from flows.models import ActivityType, Status, CandidateFlow, Activity
from jobs.models import JobPosting

class Command(BaseCommand):
    help = 'Populate initial data with junior-level names for all models'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate initial data...'))
        
        hr_companies = self.create_hr_companies()
        
        customer_companies = self.create_customer_companies()
        
        activity_types = self.create_activity_types_and_statuses()
        
        superusers = self.create_superusers()
        
        hr_users = self.create_hr_users(hr_companies, customer_companies)
        
        candidates = self.create_candidates()
        
        self.create_education_records(candidates)
        
        self.create_work_experience_records(candidates)
        
        job_postings = self.create_job_postings(hr_companies, customer_companies, hr_users)
        
        candidate_flows = self.create_candidate_flows(job_postings, candidates, hr_companies, hr_users)
        
        self.create_activities(candidate_flows, activity_types, hr_users, hr_companies)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated all initial data!'))

    def create_hr_companies(self):
        self.stdout.write('Creating HR Companies...')
        hr_companies_data = [
            {'name': 'TechBuddy HR Solutions', 'code': 'TBHR'},
            {'name': 'NextGen Talent Co', 'code': 'NGTC'},
        ]
        
        hr_companies = []
        for data in hr_companies_data:
            company, created = HRCompany.objects.get_or_create(
                code=data['code'],
                defaults={'name': data['name']}
            )
            hr_companies.append(company)
            if created:
                self.stdout.write(f'  Created HR Company: {company.name}')
            else:
                self.stdout.write(f'  HR Company already exists: {company.name}')
        
        return hr_companies

    def create_customer_companies(self):
        self.stdout.write('Creating Customer Companies...')
        customer_companies_data = [
            {'name': 'CoolStartup Inc', 'code': 'CSI'},
            {'name': 'FreshTech Labs', 'code': 'FTL'},
        ]
        
        customer_companies = []
        for data in customer_companies_data:
            company, created = CustomerCompany.objects.get_or_create(
                code=data['code'],
                defaults={'name': data['name']}
            )
            customer_companies.append(company)
            if created:
                self.stdout.write(f'  Created Customer Company: {company.name}')
            else:
                self.stdout.write(f'  Customer Company already exists: {company.name}')
        
        return customer_companies

    def create_activity_types_and_statuses(self):
        self.stdout.write('Creating Activity Types and Statuses...')
        activity_data = [
            {
                'name': 'Phone Call',
                'description': 'Phone call made to candidate',
                'statuses': [
                    'Activity Completed',
                    'Positive',
                    'Negative',
                    'Unreachable',
                    'Candidate wants to work in different field'
                ]
            },
            {
                'name': 'Email Sent',
                'description': 'Email sent to candidate',
                'statuses': [
                    'Activity Completed',
                    'Positive',
                    'Negative',
                    'Revised email sent'
                ]
            }
        ]

        activity_types = []
        for activity_info in activity_data:
            activity_type, created = ActivityType.objects.get_or_create(
                name=activity_info['name'],
                defaults={'description': activity_info['description']}
            )
            activity_types.append(activity_type)
            
            if created:
                self.stdout.write(f'  Created activity type: {activity_type.name}')
            else:
                self.stdout.write(f'  Activity type already exists: {activity_type.name}')

            for status_name in activity_info['statuses']:
                status_obj, status_created = Status.objects.get_or_create(
                    name=status_name,
                    activity_type=activity_type
                )
                
                if status_created:
                    self.stdout.write(f'    Created status: {status_name}')
        
        return activity_types

    def create_superusers(self):
        self.stdout.write('Creating Superusers...')
        superusers_data = [
            {
                'username': 'jake_admin',
                'email': 'jake.admin@wisehire.com',
                'first_name': 'Jake',
                'last_name': 'Miller',
                'phone': '+1-555-0123'
            },
            {
                'username': 'emma_super',
                'email': 'emma.super@wisehire.com',
                'first_name': 'Emma',
                'last_name': 'Davis',
                'phone': '+1-555-0456'
            }
        ]
        
        superusers = []
        for data in superusers_data:
            user, created = HRUser.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'phone': data['phone'],
                    'is_superuser': True,
                    'is_staff': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                superusers.append(user)
                self.stdout.write(f'  Created superuser: {user.username}')
            else:
                superusers.append(user)
                self.stdout.write(f'  Superuser already exists: {user.username}')
        
        return superusers

    def create_hr_users(self, hr_companies, customer_companies):
        self.stdout.write('Creating HR Users...')
        hr_users_data = [
            {
                'username': 'alex_hr',
                'email': 'alex.hr@techbuddy.com',
                'first_name': 'Alex',
                'last_name': 'Johnson',
                'phone': '+1-555-0789',
                'hr_company': hr_companies[0], 
                'authorized_companies': [customer_companies[0]] 
            },
            {
                'username': 'sam_recruiter',
                'email': 'sam.recruiter@nextgen.com',
                'first_name': 'Sam',
                'last_name': 'Wilson',
                'phone': '+1-555-0321',
                'hr_company': hr_companies[1],  
                'authorized_companies': [customer_companies[1]]
            }
        ]
        
        hr_users = []
        for data in hr_users_data:
            user, created = HRUser.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'phone': data['phone'],
                    'hr_company': data['hr_company'],
                    'is_staff': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                user.authorized_customer_companies.set(data['authorized_companies'])
                hr_users.append(user)
                self.stdout.write(f'  Created HR user: {user.username}')
            else:
                hr_users.append(user)
                self.stdout.write(f'  HR user already exists: {user.username}')
        
        return hr_users

    def create_candidates(self):
        self.stdout.write('Creating Candidates...')
        candidates_data = [
            {
                'first_name': 'Casey',
                'last_name': 'Brown',
                'email': 'casey.brown@email.com',
                'phone': '+1-555-0654',
                'address': 'Downtown, Springfield'
            },
            {
                'first_name': 'Jordan',
                'last_name': 'Taylor',
                'email': 'jordan.taylor@email.com',
                'phone': '+1-555-0987',
                'address': 'Riverside, Greenfield'
            }
        ]
        
        candidates = []
        for data in candidates_data:
            candidate, created = Candidate.objects.get_or_create(
                email=data['email'],
                defaults=data
            )
            candidates.append(candidate)
            if created:
                self.stdout.write(f'  Created candidate: {candidate.full_name}')
            else:
                self.stdout.write(f'  Candidate already exists: {candidate.full_name}')
        
        return candidates

    def create_education_records(self, candidates):
        self.stdout.write('Creating Education records...')
        education_data = [
            {
                'candidate': candidates[0],
                'school_name': 'Riverside Technical Institute',
                'department': 'Computer Engineering',
                'degree': 'Bachelor',
                'start_date': datetime(2019, 9, 1).date(),
                'end_date': datetime(2023, 6, 15).date(),
                'gpa': 3.2
            },
            {
                'candidate': candidates[1],
                'school_name': 'Greenfield University',
                'department': 'Industrial Engineering',
                'degree': 'Bachelor',
                'start_date': datetime(2018, 9, 1).date(),
                'end_date': datetime(2022, 6, 15).date(),
                'gpa': 3.5
            }
        ]
        
        for data in education_data:
            education, created = Education.objects.get_or_create(
                candidate=data['candidate'],
                school_name=data['school_name'],
                department=data['department'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  Created education: {education.candidate.full_name} - {education.school_name}')

    def create_work_experience_records(self, candidates):
        self.stdout.write('Creating Work Experience records...')
        work_experience_data = [
            {
                'candidate': candidates[0],
                'company_name': 'StartupHub',
                'position': 'Junior Developer',
                'description': 'Worked on web development projects using Django and React',
                'start_date': datetime(2023, 7, 1).date(),
                'end_date': datetime(2024, 12, 31).date()
            },
            {
                'candidate': candidates[1],
                'company_name': 'TechCorp',
                'position': 'Business Analyst Intern',
                'description': 'Analyzed business processes and created reports',
                'start_date': datetime(2022, 7, 1).date(),
                'end_date': datetime(2023, 1, 31).date()
            }
        ]
        
        for data in work_experience_data:
            work_exp, created = WorkExperience.objects.get_or_create(
                candidate=data['candidate'],
                company_name=data['company_name'],
                position=data['position'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  Created work experience: {work_exp.candidate.full_name} - {work_exp.company_name}')

    def create_job_postings(self, hr_companies, customer_companies, hr_users):
        self.stdout.write('Creating Job Postings...')
        job_postings_data = [
            {
                'title': 'Junior Frontend Developer',
                'code': 'JFD001',
                'description': 'Looking for a junior frontend developer with React experience',
                'hr_company': hr_companies[0],
                'customer_company': customer_companies[0],
                'created_by': hr_users[0],
                'closing_date': timezone.now() + timedelta(days=30)
            },
            {
                'title': 'Junior Data Analyst',
                'code': 'JDA002',
                'description': 'Seeking a junior data analyst with Python and SQL skills',
                'hr_company': hr_companies[1],
                'customer_company': customer_companies[1],
                'created_by': hr_users[1],
                'closing_date': timezone.now() + timedelta(days=45)
            }
        ]
        
        job_postings = []
        for data in job_postings_data:
            job_posting, created = JobPosting.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            job_postings.append(job_posting)
            if created:
                self.stdout.write(f'  Created job posting: {job_posting.code} - {job_posting.title}')
            else:
                self.stdout.write(f'  Job posting already exists: {job_posting.code}')
        
        return job_postings

    def create_candidate_flows(self, job_postings, candidates, hr_companies, hr_users):
        self.stdout.write('Creating Candidate Flows...')
        candidate_flows_data = [
            {
                'job_posting': job_postings[0],
                'candidate': candidates[0],
                'hr_company': hr_companies[0],
                'created_by': hr_users[0],
                'notes': 'Candidate looks promising for frontend role'
            },
            {
                'job_posting': job_postings[1],
                'candidate': candidates[1],
                'hr_company': hr_companies[1],
                'created_by': hr_users[1],
                'notes': 'Good analytical skills, suitable for data analyst position'
            }
        ]
        
        candidate_flows = []
        for data in candidate_flows_data:
            candidate_flow, created = CandidateFlow.objects.get_or_create(
                job_posting=data['job_posting'],
                candidate=data['candidate'],
                defaults=data
            )
            candidate_flows.append(candidate_flow)
            if created:
                self.stdout.write(f'  Created candidate flow: {candidate_flow}')
            else:
                self.stdout.write(f'  Candidate flow already exists: {candidate_flow}')
        
        return candidate_flows

    def create_activities(self, candidate_flows, activity_types, hr_users, hr_companies):
        self.stdout.write('Creating Activities...')
        
        phone_statuses = Status.objects.filter(activity_type__name='Phone Call')
        email_statuses = Status.objects.filter(activity_type__name='Email Sent')
        
        if not phone_statuses.exists() or not email_statuses.exists():
            self.stdout.write(self.style.WARNING('  No statuses found, skipping activity creation'))
            return
        
        activities_data = [
            {
                'candidate_flow': candidate_flows[0],
                'activity_type': activity_types[0],  
                'status': phone_statuses.filter(name='Positive').first(),
                'created_by': hr_users[0],
                'hr_company': hr_companies[0],
                'notes': 'Had a great conversation with Casey, very interested in the position'
            },
            {
                'candidate_flow': candidate_flows[1],
                'activity_type': activity_types[1], 
                'status': email_statuses.filter(name='Activity Completed').first(),
                'created_by': hr_users[1],
                'hr_company': hr_companies[1],
                'notes': 'Sent initial screening email to Jordan'
            }
        ]
        
        for data in activities_data:
            if data['status']:  
                activity, created = Activity.objects.get_or_create(
                    candidate_flow=data['candidate_flow'],
                    activity_type=data['activity_type'],
                    status=data['status'],
                    created_by=data['created_by'],
                    defaults=data
                )
                if created:
                    self.stdout.write(f'  Created activity: {activity}')
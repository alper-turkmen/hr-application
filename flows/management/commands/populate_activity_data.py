from django.core.management.base import BaseCommand
from flows.models import ActivityType, Status

class Command(BaseCommand):
    help = 'Populate initial activity types and statuses'

    def handle(self, *args, **options):
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
            },
            {
                'name': 'Test Sent',
                'description': 'Test sent to candidate',
                'statuses': [
                    'Activity Completed',
                    'Successful',
                    'Failed'
                ]
            }
        ]

        for activity_info in activity_data:
            activity_type, created = ActivityType.objects.get_or_create(
                name=activity_info['name'],
                defaults={'description': activity_info['description']}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created activity type: {activity_type.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Activity type already exists: {activity_type.name}')
                )

            for status_name in activity_info['statuses']:
                status_obj, status_created = Status.objects.get_or_create(
                    name=status_name,
                    activity_type=activity_type
                )
                
                if status_created:
                    self.stdout.write(
                        self.style.SUCCESS(f'  Created status: {status_name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  Status already exists: {status_name}')
                    )

        self.stdout.write(
            self.style.SUCCESS('Successfully populated activity types and statuses')
        )
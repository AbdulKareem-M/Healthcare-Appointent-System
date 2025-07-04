from django.core.management.base import BaseCommand
from appointments.models import Doctor

class Command(BaseCommand):
    help = 'Update consultation fees for doctors'
    
    def add_arguments(self, parser):
        parser.add_argument('--default-fee', type=float, default=500.0, help='Default consultation fee')
    
    def handle(self, *args, **options):
        default_fee = options['default_fee']
        
        # Update all doctors with default fee if not set
        doctors_updated = Doctor.objects.filter(consultation_fee__isnull=True).update(
            consultation_fee=default_fee
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Updated {doctors_updated} doctors with consultation fee of ₹{default_fee}')
        )

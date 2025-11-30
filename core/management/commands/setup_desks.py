from django.core.management.base import BaseCommand
from core.models import Desk

class Command(BaseCommand):
    help = 'Populates the database with 24 desks in a 4x6 grid'

    def handle(self, *args, **kwargs):
        # Check if desks already exist
        if Desk.objects.exists():
            count = Desk.objects.count()
            self.stdout.write(self.style.WARNING(f'Desks already exist ({count} desks found). Skipping setup.'))
            return
        
        # Create desks only if none exist
        rows = 4
        cols = 6
        count = 1
        
        for r in range(rows):
            for c in range(cols):
                Desk.objects.create(
                    name=f"Desk {count}",
                    row=r,
                    col=c
                )
                count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count-1} desks'))

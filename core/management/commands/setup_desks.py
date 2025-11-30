from django.core.management.base import BaseCommand
from core.models import Desk

class Command(BaseCommand):
    help = 'Populates the database with 24 desks in a 4x6 grid'

    def handle(self, *args, **kwargs):

        
        # Create desks only if none exist
        # Define desk coordinates (x, y in percentages)
        desks_data = [
            # Top Left Cluster
            {"name": "Desk 1", "x": 30, "y": 4},
            {"name": "Desk 2", "x": 41, "y": 4},
            {"name": "Desk 3", "x": 30, "y": 14},
            {"name": "Desk 4", "x": 41, "y": 14},

            # Top Right Area
            {"name": "Desk 5", "x": 75, "y": 14},

            {"name": "Desk 6", "x": 75, "y": 27},
            {"name": "Desk 7", "x": 86, "y": 27},

            # Middle Right Column
            {"name": "Desk 8", "x": 75, "y": 42},
            {"name": "Desk 9", "x": 86, "y": 42},
            {"name": "Desk 10", "x": 75, "y": 52},
            {"name": "Desk 11", "x": 86, "y": 52},
            {"name": "Desk 14", "x": 75, "y": 65},
            {"name": "Desk 15", "x": 86, "y": 65},
            {"name": "Desk 18", "x": 75, "y": 75},
            {"name": "Desk 19", "x": 86, "y": 75},

            # Middle Left Block
            {"name": "Desk 12", "x": 30, "y": 50},
            {"name": "Desk 13", "x": 41, "y": 50},
            {"name": "Desk 16", "x": 30, "y": 60},
            {"name": "Desk 17", "x": 41, "y": 60},

            # Bottom Right
            {"name": "Desk 20", "x": 86, "y": 95},
            {"name": "Desk 21", "x": 86, "y": 105},
        ]

        # Clear existing desks to reset layout
        # Update existing desks or create new ones
        updated_count = 0
        created_count = 0
        
        for desk_info in desks_data:
            obj, created = Desk.objects.update_or_create(
                name=desk_info["name"],
                defaults={
                    'x': desk_info["x"],
                    'y': desk_info["y"]
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} desks and created {created_count} desks.'))

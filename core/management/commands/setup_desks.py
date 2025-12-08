from django.core.management.base import BaseCommand
from core.models import Desk

class Command(BaseCommand):
    help = 'Populates the database with 24 desks in a 4x6 grid'

    def handle(self, *args, **kwargs):

        
        # Create desks only if none exist
        # Define desk coordinates (x, y in percentages)
        desks_data = [
            # Top room area
            {"number" : "1", "name": "Desk 1", "x": 19, "y": 3},
            {"number" : "2", "name": "Desk 2", "x": 32, "y": 3},
            {"number" : "3", "name": "Desk 3", "x": 19, "y": 9},
            {"number" : "4", "name": "Desk 4", "x": 32, "y": 9},
            {"number" : "5", "name": "Desk 5", "x": 51, "y": 3},
            {"number" : "6", "name": "Desk 6", "x": 75, "y": 15},

            # Middle Left Block
            {"number" : "7", "name": "Desk 7", "x": 34.5, "y": 44},
            {"number" : "8", "name": "Desk 8", "x": 49.5, "y": 44},
            {"number" : "9", "name": "Desk 9", "x": 34.5, "y": 51},
            {"number" : "10", "name": "Desk 10", "x": 49.5, "y": 51},

            # Middle right area
            {"number" : "11", "name": "Desk 11", "x": 76, "y": 22.5},
            {"number" : "12", "name": "Desk 12", "x": 91, "y": 22.5},
            {"number" : "13", "name": "Desk 13", "x": 76, "y": 29.5},
            {"number" : "14", "name": "Desk 14", "x": 91, "y": 29.5},

            {"number" : "15", "name": "Desk 15", "x": 76, "y": 37},
            {"number" : "16", "name": "Desk 16", "x": 91, "y": 37},

            {"number" : "17", "name": "Desk 17", "x": 76, "y": 44},
            {"number" : "18", "name": "Desk 18", "x": 91, "y": 44},
            {"number" : "19", "name": "Desk 19", "x": 76, "y": 51},
            {"number" : "20", "name": "Desk 20", "x": 91, "y": 51},

            {"number" : "21", "name": "Desk 21", "x": 76, "y": 58},
            {"number" : "22", "name": "Desk 22", "x": 91, "y": 58},
            {"number" : "23", "name": "Desk 23", "x": 76, "y": 65},
            {"number" : "24", "name": "Desk 24", "x": 91, "y": 65},

            # Bottom Right
            {"number" : "25", "name": "Desk 25", "x": 91, "y": 85},
            {"number" : "26", "name": "Desk 26", "x": 91, "y": 91},
        ]

        # Clear existing desks to reset layout
        # Update existing desks or create new ones
        updated_count = 0
        created_count = 0
        
        for desk_info in desks_data:
            obj, created = Desk.objects.update_or_create(
                name=desk_info["name"],
                defaults={
                    'number': desk_info["number"],
                    'x': desk_info["x"],
                    'y': desk_info["y"]
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} desks and created {created_count} desks.'))

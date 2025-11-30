from django.core.management.base import BaseCommand
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = 'Import products from products_export.json'

    def handle(self, *args, **options):
        # Path to the JSON file in the project root
        # In Railway, we're in /app, and ecommerce_backend is a subdirectory
        # products_export.json is at /app/products_export.json
        json_path = '/app/products_export.json'
        
        # Fallback to relative path for local development
        if not os.path.exists(json_path):
            json_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), 
                '..', '..', '..', '..', 
                'products_export.json'
            ))
        
        self.stdout.write(self.style.WARNING(f'Looking for products_export.json at: {json_path}'))
        
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f'File not found: {json_path}'))
            self.stdout.write(self.style.WARNING('Skipping import - file not found'))
            return
        
        self.stdout.write(self.style.SUCCESS('Found products_export.json'))
        self.stdout.write('Loading data...')
        
        try:
            call_command('loaddata', json_path)
            self.stdout.write(self.style.SUCCESS('Successfully imported products!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing products: {e}'))

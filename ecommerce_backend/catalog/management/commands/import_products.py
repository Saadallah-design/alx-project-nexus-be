from django.core.management.base import BaseCommand
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = 'Import products from products_export.json'

    def handle(self, *args, **options):
        # Path to the JSON file (one level up from ecommerce_backend)
        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '..', 'products_export.json')
        
        self.stdout.write(self.style.WARNING(f'Looking for products_export.json at: {json_path}'))
        
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f'File not found: {json_path}'))
            return
        
        self.stdout.write(self.style.SUCCESS('Found products_export.json'))
        self.stdout.write('Loading data...')
        
        try:
            call_command('loaddata', json_path)
            self.stdout.write(self.style.SUCCESS('Successfully imported products!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing products: {e}'))

from django.core.management import call_command
from django.core.management.base import BaseCommand
import sys

class Command(BaseCommand):
    help = 'Validates migrations before applying'

    def handle(self, *args, **options):
        try:
            # Check for conflicting migrations
            call_command('check', deploy=True)
            self.stdout.write("Validation successful. Proceeding...")
        except Exception as e:
            self.stderr.write(f"Pre-migration check failed: {e}")
            sys.exit(1)
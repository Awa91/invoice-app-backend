from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = 'Checks the database connection'

    def handle(self, *args, **options):
        self.stdout.write('Testing database connection...')
        db_conn = connections['default']
        try:
            db_conn.cursor()
        except OperationalError:
            self.stderr.write(self.style.ERROR("Database connection failed!"))
            exit(1)
        else:
            self.stdout.write(self.style.SUCCESS("Database connection successful."))
            exit(0)
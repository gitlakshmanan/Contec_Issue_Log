from django.core.management.base import BaseCommand
from django.db import connection, transaction
from base.models import Issue


class Command(BaseCommand):
    help = "Delete all Issue rows and reset the autoincrement sequence (SQLite)."

    def handle(self, *args, **options):
        self.stdout.write("Deleting all issues...")
        with transaction.atomic():
            Issue.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("All issues deleted."))

        # Reset SQLite sequence so next insert starts at 1
        try:
            if connection.vendor == 'sqlite':
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM sqlite_sequence WHERE name=%s", ['base_issue'])
                self.stdout.write(self.style.SUCCESS('SQLite sequence reset for base_issue.'))
            else:
                self.stdout.write(self.style.WARNING('Sequence reset only implemented for SQLite.'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not reset sequence: {e}'))

        self.stdout.write(self.style.SUCCESS("Database cleared and sequence reset."))

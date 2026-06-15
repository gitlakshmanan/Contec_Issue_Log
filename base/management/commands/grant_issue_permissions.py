"""
Management command to grant issue permissions to a user
Usage: python manage.py grant_issue_permissions <username>
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from base.models import Issue


class Command(BaseCommand):
    help = 'Grant all issue permissions to a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to grant permissions to')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
            return
        
        # Get content type for Issue model
        content_type = ContentType.objects.get_for_model(Issue)
        
        # List of permissions to grant
        permission_codenames = [
            'can_view_issue',
            'can_add_issue',
            'can_change_issue',
            'can_delete_issue',
            'can_export_issue',
            'can_import_issue',
        ]
        
        granted_count = 0
        for codename in permission_codenames:
            try:
                permission = Permission.objects.get(
                    codename=codename,
                    content_type=content_type
                )
                user.user_permissions.add(permission)
                self.stdout.write(self.style.SUCCESS(f'✓ Granted: {codename}'))
                granted_count += 1
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'✗ Permission not found: {codename}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully granted {granted_count} permissions to {username}'))
        self.stdout.write(self.style.SUCCESS(f'{username} can now create, view, edit, and delete issues!'))

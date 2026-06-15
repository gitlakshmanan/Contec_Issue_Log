from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from base.models import UserProfile


class Command(BaseCommand):
    help = 'Set up admin user with proper permissions and approve their account'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            admin_user.set_password('admin123')  # Change this password in production!
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS('Admin user created successfully!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Admin user already exists.')
            )
        
        # Get or create UserProfile for admin
        try:
            admin_profile = admin_user.profile
        except UserProfile.DoesNotExist:
            admin_profile = UserProfile.objects.create(
                user=admin_user,
                status='approved',
                department='Administration',
                approved_by=admin_user,
            )
            self.stdout.write(
                self.style.SUCCESS('Admin profile created successfully!')
            )
        
        # Ensure admin profile is approved
        if admin_profile.status != 'approved':
            admin_profile.status = 'approved'
            admin_profile.approved_by = admin_user
            admin_profile.save()
            self.stdout.write(
                self.style.SUCCESS('Admin profile approved successfully!')
            )
        
        # Assign all permissions to admin user
        all_permissions = Permission.objects.all()
        admin_user.user_permissions.set(all_permissions)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Admin user setup complete! Username: admin, Password: admin123'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                'IMPORTANT: Change the admin password in production!'
            )
        )

from django.core.management.base import BaseCommand
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Force-create grootadmin superuser with known password'
    def handle(self, *args, **options):
        # We use update_or_create to be 100% sure the password matches
        user, created = CustomUser.objects.get_or_create(username='grootadmin')
        user.email = 'grootadmin@pme.eu'
        user.set_password('pmeadmin2026')
        user.is_superuser = True
        user.is_staff = True
        user.role = CustomUser.Role.SUPERUSER
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully forced credentials for grootadmin (New: {created})'))

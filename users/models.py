from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import School
from gamification.models import UserProgression


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        SUPERUSER     = 'SUPERUSER',     'Platform Superuser'
        SCHOOL_ADMIN  = 'SCHOOL_ADMIN',  'School Admin'
        STUDENT       = 'STUDENT',       'Paid Student'
        GUEST         = 'GUEST',         'Guest Visitor'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.GUEST
    )
    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text="The school this user belongs to."
    )

    def is_school_admin(self):
        return self.role == self.Role.SCHOOL_ADMIN

    def is_platform_superuser(self):
        return self.role == self.Role.SUPERUSER

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


@receiver(post_save, sender=CustomUser)
def handle_user_creation(sender, instance, created, **kwargs):
    if created:
        UserProgression.objects.get_or_create(user=instance)
        if instance.role in [CustomUser.Role.SCHOOL_ADMIN, CustomUser.Role.SUPERUSER]:
            instance.is_staff = True
            CustomUser.objects.filter(pk=instance.pk).update(is_staff=True)

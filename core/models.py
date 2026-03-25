from django.db import models


class School(models.Model):
    """Represents a language school or institution using the platform."""
    code = models.CharField(max_length=20, unique=True, help_text="Unique school code (e.g., GLS, BSPR)")
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default="#CC0000", help_text="Hex color for branding")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "School"
        verbose_name_plural = "Schools"


class SchoolScopedManager(models.Manager):
    def for_user(self, user):
        """Returns a queryset filtered by the user's school, unless superuser."""
        if user.is_authenticated and (user.is_superuser or user.role == 'SUPERUSER'):
            return self.all()
        if user.is_authenticated and user.school:
            return self.filter(school=user.school)
        return self.none()


class SchoolScopedModel(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="%(class)s_items"
    )

    objects = SchoolScopedManager()

    class Meta:
        abstract = True

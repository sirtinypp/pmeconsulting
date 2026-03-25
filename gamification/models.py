from django.db import models


class UserProgression(models.Model):
    user = models.OneToOneField(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='progression'
    )
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - Level {self.level} ({self.points} pts)"

    def add_points(self, amount):
        self.points += amount
        # Simple levelling: every 100 points = 1 level
        self.level = max(1, self.points // 100 + 1)
        self.save()

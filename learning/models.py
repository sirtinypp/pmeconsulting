from django.db import models
from core.models import SchoolScopedModel


class Course(SchoolScopedModel):
    """A German language course (e.g., A1 Beginner, B2 Advanced)."""
    LEVEL_CHOICES = [
        ('A1', 'A1 — Beginner'),
        ('A2', 'A2 — Elementary'),
        ('B1', 'B1 — Intermediate'),
        ('B2', 'B2 — Upper Intermediate'),
        ('C1', 'C1 — Advanced'),
        ('C2', 'C2 — Mastery'),
        ('CUSTOM', 'Custom'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='A1')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration = models.CharField(max_length=100, blank=True, help_text="e.g., 8 weeks, 40 hours")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} [{self.level}] ({self.school.code})"


class Lesson(models.Model):
    """A single lesson/module within a Course."""
    class LessonType(models.TextChoices):
        VIDEO    = 'VID', 'Video Lesson'
        READING  = 'DOC', 'Reading Material'
        EXERCISE = 'EXC', 'Exercise'
        QUIZ     = 'QIZ', 'Quiz'
        SPEAKING = 'SPK', 'Speaking Practice'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    lesson_type = models.CharField(max_length=3, choices=LessonType.choices, default=LessonType.READING)
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    video_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class LessonResource(models.Model):
    class ResourceType(models.TextChoices):
        DOCUMENT = 'DOC', 'Document (PDF/DOC)'
        VIDEO    = 'VID', 'Video Link'
        LINK     = 'URL', 'External Link'

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=3, choices=ResourceType.choices, default=ResourceType.DOCUMENT)
    file = models.FileField(upload_to='lesson_materials/', null=True, blank=True)
    url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.title} — {self.get_resource_type_display()}"


class TrainingEvent(SchoolScopedModel):
    """A live session, workshop, or cultural event."""
    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.title} — {self.date.date()} ({self.school.code})"


class CourseEnrollment(models.Model):
    class Status(models.TextChoices):
        ENROLLED    = 'ENROLLED',    'Enrolled'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED   = 'COMPLETED',   'Completed'

    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ENROLLED)
    progress_percent = models.IntegerField(default=0)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} — {self.course.title} ({self.status})"


class LessonCompletion(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='lesson_completions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')


class Achievement(SchoolScopedModel):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=255)
    description = models.TextField()
    earned_at = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)
    icon = models.CharField(max_length=50, default="🏆")

    def __str__(self):
        return f"{self.user.username} — {self.title}"


class QuizQuestion(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q: {self.text[:50]}..."


class QuizChoice(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.id} — {self.text}"


class QuizAttempt(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    passed = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')

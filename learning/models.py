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
    CATEGORY_CHOICES = [
        ('LANG', 'Language Course'),
        ('LMS', 'LMS'),
        ('EXM', 'Exam Preparation Course'),
        ('OTH', 'Others'),
    ]
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=4, choices=CATEGORY_CHOICES, default='LANG')
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    description = models.TextField()
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='A1')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration = models.CharField(max_length=100, blank=True, help_text="e.g., 8 weeks, 40 hours")
    is_active = models.BooleanField(default=True)
    show_in_catalog = models.BooleanField(default=True, help_text="Show this course in the public/school course catalog for non-enrolled students")
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
    video_url = models.URLField(max_length=500, blank=True, null=True)
    is_final_exam = models.BooleanField(default=False, help_text="If true, this quiz acts as the course completion exam.")
    duration_minutes = models.PositiveIntegerField(default=30, help_text="Time limit in minutes (for quizzes/exams).")

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


class LessonActivity(models.Model):
    """An interactive task or assignment within a lesson."""
    class ActivityType(models.TextChoices):
        ASSIGNMENT = 'ASN', 'Assignment/Submission'
        INTERACTIVE = 'INT', 'Interactive Task'
        REFLECTION  = 'REF', 'Reflection/Journal'
        PRACTICE    = 'PRC', 'Practice Session'

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='activities')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    activity_type = models.CharField(max_length=3, choices=ActivityType.choices, default=ActivityType.PRACTICE)
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Lesson Activities"

    def __str__(self):
        return f"{self.lesson.title} Activity: {self.title}"


class TrainingEvent(SchoolScopedModel):
    """A live session, workshop, or cultural event."""
    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.title} — {self.date.date()} ({self.school.code})"


class ActivitySubmission(models.Model):
    """A student submission for a lesson activity."""
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='activity_submissions')
    activity = models.ForeignKey(LessonActivity, on_delete=models.CASCADE, related_name='submissions')
    submission_text = models.TextField(blank=True, help_text="Text-based answer or reflection")
    submission_url = models.URLField(blank=True, null=True, help_text="Link to external work (e.g., Google Drive, Dropbox)")
    submission_file = models.FileField(upload_to='activity_submissions/', null=True, blank=True, help_text="Supports Audio (MP3/WAV), PDF, or Images")
    status = models.CharField(max_length=20, default='PENDING', choices=[
        ('PENDING', 'Pending Review'),
        ('GRADED', 'Graded/Reviewed'),
        ('RESUBMIT', 'Requires Resubmission')
    ])
    feedback = models.TextField(blank=True)
    grade = models.IntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'activity')

    def __str__(self):
        return f"{self.user.username} - {self.activity.title}"


class CourseEnrollment(models.Model):
    class Status(models.TextChoices):
        PENDING     = 'PENDING',     'Pending Approval'
        ENROLLED    = 'ENROLLED',    'Enrolled'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED   = 'COMPLETED',   'Completed'
        REJECTED    = 'REJECTED',    'Rejected'

    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    progress_percent = models.IntegerField(default=0)
    admin_note = models.TextField(blank=True, null=True, help_text="Custom message from admin regarding this enrollment status")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} — {self.course.title} ({self.status})"


class CourseTier(models.Model):
    """Pricing Tier for a German language course level (Basic, Standard, Premium)."""
    TIER_CHOICES = [
        ('BASIC', 'Basic'),
        ('STANDARD', 'Standard'),
        ('PREMIUM', 'Premium'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='tiers')
    tier_type = models.CharField(max_length=10, choices=TIER_CHOICES, default='BASIC')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in PHP")
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('course', 'tier_type')

    def __str__(self):
        return f"{self.course.title} [{self.tier_type}] — ₱{self.price:,.2f}"


class PaymentOrder(models.Model):
    """Tracks payment transaction for course enrollment via PayMongo."""
    class PaymentStatus(models.TextChoices):
        PENDING   = 'PENDING',  'Pending Payment'
        PAID      = 'PAID',     'Paid'
        FAILED    = 'FAILED',   'Failed'
        REFUNDED  = 'REFUNDED', 'Refunded'

    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='payment_orders')
    enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE, related_name='payment_orders')
    tier = models.ForeignKey(CourseTier, on_delete=models.SET_NULL, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in PHP")
    currency = models.CharField(max_length=3, default='PHP')
    
    provider = models.CharField(max_length=20, default='paymongo')
    checkout_session_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    checkout_url = models.URLField(max_length=500, blank=True, null=True)
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    
    status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} — {self.user.username} — {self.amount} {self.currency} ({self.status})"



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
    image = models.ImageField(upload_to='quiz_images/', blank=True, null=True)
    audio = models.FileField(upload_to='quiz_audio/', blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True, null=True)

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

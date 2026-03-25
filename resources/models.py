from django.db import models
from django.utils.text import slugify


class Post(models.Model):
    class Category(models.TextChoices):
        DIY_GUIDE = 'DIY', 'DIY Guide'
        ARTICLE   = 'ART', 'Article'
        NEWS      = 'NEWS', 'News & Updates'

    title       = models.CharField(max_length=255)
    slug        = models.SlugField(max_length=255, unique=True, blank=True)
    category    = models.CharField(max_length=5, choices=Category.choices, default=Category.ARTICLE)
    excerpt     = models.TextField(help_text="Short summary shown on the list page")
    content     = models.TextField(help_text="Full post body (HTML or plain text)")
    cover_emoji = models.CharField(max_length=10, default="📄", help_text="Emoji used as cover art")
    author      = models.CharField(max_length=100, default="PME Consulting EU")
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

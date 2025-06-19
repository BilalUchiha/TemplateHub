from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
import os

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('templates:category_templates', kwargs={'slug': self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


def template_upload_path(instance, filename):
    """Generate upload path for template files"""
    return f'templates/{instance.author.username}/{instance.slug}/{filename}'


def template_preview_path(instance, filename):
    """Generate upload path for template preview images"""
    return f'previews/{instance.author.username}/{instance.slug}/{filename}'


class Template(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, help_text="Brief description for listings")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='templates')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='templates')
    tags = models.ManyToManyField(Tag, blank=True, related_name='templates')

    # File and preview
    template_file = models.FileField(upload_to=template_upload_path, help_text="Upload ZIP file containing template")
    preview_image = models.ImageField(upload_to=template_preview_path, blank=True, null=True)
    demo_url = models.URLField(blank=True, help_text="Live demo URL")

    # Metadata
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    version = models.CharField(max_length=20, default='1.0.0')
    file_size = models.PositiveIntegerField(blank=True, null=True, help_text="File size in bytes")
    download_count = models.PositiveIntegerField(default=0)

    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Calculate file size if template_file exists
        if self.template_file and not self.file_size:
            self.file_size = self.template_file.size

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('templates:template_detail', kwargs={'pk': self.pk})

    def get_file_size_display(self):
        """Return human readable file size"""
        if not self.file_size:
            return "Unknown"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"

    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    @property
    def review_count(self):
        """Get total number of reviews"""
        return self.reviews.count()


class TemplateDownload(models.Model):
    """Track template downloads"""
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='downloads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downloads', null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-downloaded_at']

    def __str__(self):
        user_info = self.user.username if self.user else self.ip_address
        return f"{user_info} downloaded {self.template.title}"


class TemplateFavorite(models.Model):
    """User favorites/bookmarks"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'template')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} favorited {self.template.title}"


class TemplateView(models.Model):
    """Track template page views"""
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        user_info = self.user.username if self.user else self.ip_address
        return f"{user_info} viewed {self.template.title}"

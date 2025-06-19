from django.contrib import admin
from .models import Category, Tag, Template, TemplateDownload, TemplateFavorite, TemplateView

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'difficulty', 'download_count', 'created_at']
    list_filter = ['status', 'difficulty', 'category', 'is_featured', 'is_free', 'created_at']
    search_fields = ['title', 'description', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['download_count', 'file_size', 'created_at', 'updated_at']
    actions = ['publish_templates', 'reject_templates']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'author', 'category', 'tags')
        }),
        ('Files and Media', {
            'fields': ('template_file', 'preview_image', 'demo_url')
        }),
        ('Metadata', {
            'fields': ('difficulty', 'version', 'file_size', 'status', 'is_featured', 'is_free', 'price')
        }),
        ('Statistics', {
            'fields': ('download_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def publish_templates(self, request, queryset):
        """Publish selected templates"""
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} template(s) successfully published.')
    publish_templates.short_description = "Publish selected templates"

    def reject_templates(self, request, queryset):
        """Reject selected templates"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} template(s) rejected.')
    reject_templates.short_description = "Reject selected templates"

@admin.register(TemplateDownload)
class TemplateDownloadAdmin(admin.ModelAdmin):
    list_display = ['template', 'user', 'ip_address', 'downloaded_at']
    list_filter = ['downloaded_at']
    search_fields = ['template__title', 'user__username', 'ip_address']
    readonly_fields = ['downloaded_at']

@admin.register(TemplateFavorite)
class TemplateFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'template', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'template__title']

@admin.register(TemplateView)
class TemplateViewAdmin(admin.ModelAdmin):
    list_display = ['template', 'user', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['template__title', 'user__username', 'ip_address']
    readonly_fields = ['viewed_at']

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, Http404, FileResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from .models import Template, Category, Tag, TemplateDownload, TemplateView, TemplateFavorite
from .forms import TemplateUploadForm, TemplateEditForm, TemplateSearchForm
import os

# Create your views here.

def home(request):
    # Get top 10 most rated templates (published only)
    top_rated_templates = Template.objects.filter(
        status='published'
    ).select_related('category', 'author').annotate(
        avg_rating=Avg('reviews__rating'),
        total_reviews=Count('reviews')
    ).filter(
        total_reviews__gt=0  # Only templates with at least one review
    ).order_by('-avg_rating', '-total_reviews')[:10]

    # If we don't have enough top-rated templates, fill with recent ones
    if top_rated_templates.count() < 6:
        # Get recent templates that aren't already in top_rated
        top_rated_ids = [t.id for t in top_rated_templates]
        recent_templates = Template.objects.filter(
            status='published'
        ).exclude(id__in=top_rated_ids).select_related('category', 'author').annotate(
            avg_rating=Avg('reviews__rating'),
            total_reviews=Count('reviews')
        ).order_by('-created_at')[:6-top_rated_templates.count()]

        # Combine the lists
        featured_templates = list(top_rated_templates) + list(recent_templates)
    else:
        featured_templates = top_rated_templates

    # Get all categories
    categories = Category.objects.all()[:12]

    # Get some stats (you can make these dynamic later)
    context = {
        'featured_templates': featured_templates,  # Now showing top-rated + recent
        'categories': categories,
        'total_templates': Template.objects.filter(status='published').count(),
        'total_downloads': sum(t.download_count for t in Template.objects.filter(status='published')),
        'total_users': User.objects.count(),
        'total_categories': categories.count(),
    }

    return render(request, 'home.html', context)

def template_list(request):
    # Get search form
    form = TemplateSearchForm(request.GET)
    templates = Template.objects.filter(status='published').select_related('category', 'author')

    # Apply filters
    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        difficulty = form.cleaned_data.get('difficulty')
        is_free = form.cleaned_data.get('is_free')

        if q:
            templates = templates.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(short_description__icontains=q) |
                Q(tags__name__icontains=q)
            ).distinct()

        if category:
            templates = templates.filter(category=category)

        if difficulty:
            templates = templates.filter(difficulty=difficulty)

        if is_free == 'true':
            templates = templates.filter(is_free=True)
        elif is_free == 'false':
            templates = templates.filter(is_free=False)

    # Pagination
    paginator = Paginator(templates, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj,
        'templates': page_obj,
    }
    return render(request, 'templates/template_list.html', context)


def template_detail(request, pk):
    # Allow authors to see their own pending templates, others only see published
    if request.user.is_authenticated:
        template = get_object_or_404(
            Template,
            Q(pk=pk) & (Q(status='published') | Q(author=request.user))
        )
    else:
        template = get_object_or_404(Template, pk=pk, status='published')

    # Record view
    if request.user.is_authenticated:
        TemplateView.objects.get_or_create(
            template=template,
            user=request.user,
            defaults={'ip_address': get_client_ip(request)}
        )
    else:
        TemplateView.objects.create(
            template=template,
            ip_address=get_client_ip(request)
        )

    # Check if user has already reviewed this template
    user_has_reviewed = False
    is_favorited = False
    if request.user.is_authenticated:
        from reviews.models import Review
        user_has_reviewed = Review.objects.filter(
            template=template,
            user=request.user
        ).exists()

        # Check if user has favorited this template
        is_favorited = TemplateFavorite.objects.filter(
            template=template,
            user=request.user
        ).exists()

    # Get related templates
    related_templates = Template.objects.filter(
        category=template.category,
        status='published'
    ).exclude(pk=template.pk)[:4]

    context = {
        'template': template,
        'related_templates': related_templates,
        'user_has_reviewed': user_has_reviewed,
        'is_favorited': is_favorited,
    }
    return render(request, 'templates/template_detail.html', context)


@login_required
def template_upload(request):
    if request.method == 'POST':
        form = TemplateUploadForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save(commit=False)
            template.author = request.user
            template.status = 'pending'  # Set to pending for review
            template.save()
            form.save_m2m()  # Save many-to-many relationships

            messages.success(request, f'Template "{template.title}" uploaded successfully! It will be reviewed before publication.')
            return redirect('templates:template_detail', pk=template.pk)
    else:
        form = TemplateUploadForm()

    return render(request, 'templates/template_upload.html', {'form': form})


def category_templates(request, slug):
    category = get_object_or_404(Category, slug=slug)
    templates = Template.objects.filter(
        category=category,
        status='published'
    ).select_related('author')

    # Get related categories (exclude current category)
    related_categories = Category.objects.exclude(pk=category.pk)[:6]

    # Pagination
    paginator = Paginator(templates, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
        'templates': page_obj,
        'related_categories': related_categories,
    }
    return render(request, 'templates/category_templates.html', context)


def search_templates(request):
    return redirect('templates:template_list')


@login_required
def download_template(request, pk):
    template = get_object_or_404(Template, pk=pk, status='published')

    if not template.template_file:
        raise Http404("Template file not found")

    # Record download
    TemplateDownload.objects.create(
        template=template,
        user=request.user,
        ip_address=get_client_ip(request)
    )

    # Increment download count
    template.download_count += 1
    template.save(update_fields=['download_count'])

    # Return file response
    response = FileResponse(
        template.template_file.open('rb'),
        as_attachment=True,
        filename=f"{template.slug}.zip"
    )
    return response


@login_required
@require_POST
def toggle_favorite(request, pk):
    """AJAX view to toggle favorite status of a template"""
    template = get_object_or_404(Template, pk=pk, status='published')

    favorite, created = TemplateFavorite.objects.get_or_create(
        user=request.user,
        template=template
    )

    if not created:
        favorite.delete()
        is_favorited = False
    else:
        is_favorited = True

    return JsonResponse({
        'is_favorited': is_favorited,
        'favorites_count': template.favorited_by.count()
    })


@login_required
def user_favorites(request):
    """Display user's favorite templates"""
    favorites = TemplateFavorite.objects.filter(
        user=request.user
    ).select_related('template__category', 'template__author')

    # Pagination
    paginator = Paginator(favorites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'favorites': page_obj,
    }
    return render(request, 'templates/user_favorites.html', context)


def trending_templates(request):
    """Display trending templates based on recent downloads and views"""
    # Get templates with high activity in the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)

    trending = Template.objects.filter(
        status='published'
    ).annotate(
        recent_downloads=Count(
            'downloads',
            filter=Q(downloads__downloaded_at__gte=thirty_days_ago)
        ),
        recent_views=Count(
            'views',
            filter=Q(views__viewed_at__gte=thirty_days_ago)
        ),
        avg_rating=Avg('reviews__rating')
    ).order_by('-recent_downloads', '-recent_views', '-avg_rating')

    # Pagination
    paginator = Paginator(trending, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'templates': page_obj,
        'page_title': 'Trending Templates',
        'page_description': 'Most popular templates in the last 30 days'
    }
    return render(request, 'templates/template_list.html', context)


def recent_templates(request):
    """Display recently uploaded templates"""
    recent = Template.objects.filter(
        status='published'
    ).order_by('-created_at')

    # Pagination
    paginator = Paginator(recent, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'templates': page_obj,
        'page_title': 'Recent Templates',
        'page_description': 'Latest templates added to TemplateHub'
    }
    return render(request, 'templates/template_list.html', context)


def compare_templates(request):
    """Compare multiple templates side by side"""
    template_ids = request.GET.getlist('templates')
    templates = []

    if template_ids:
        templates = Template.objects.filter(
            pk__in=template_ids,
            status='published'
        ).select_related('category', 'author')[:4]  # Limit to 4 templates

    context = {
        'templates': templates,
        'template_ids': template_ids,
    }
    return render(request, 'templates/compare_templates.html', context)


def template_api(request, pk):
    """API endpoint to get template data for comparison"""
    template = get_object_or_404(Template, pk=pk, status='published')

    data = {
        'id': template.pk,
        'title': template.title,
        'short_description': template.short_description,
        'category': template.category.name,
        'author': template.author.username,
        'difficulty': template.get_difficulty_display(),
        'version': template.version,
        'price': float(template.price) if not template.is_free else 0,
        'is_free': template.is_free,
        'download_count': template.download_count,
        'average_rating': template.average_rating,
        'review_count': template.review_count,
        'tags': [tag.name for tag in template.tags.all()],
        'preview_image': template.preview_image.url if template.preview_image else None,
        'demo_url': template.demo_url,
        'created_at': template.created_at.strftime('%Y-%m-%d'),
        'file_size': template.get_file_size_display(),
        'url': template.get_absolute_url(),
    }

    return JsonResponse(data)


@login_required
def my_templates(request):
    """Display user's own templates (all statuses)"""
    user_templates = Template.objects.filter(
        author=request.user
    ).select_related('category').order_by('-created_at')

    # Pagination
    paginator = Paginator(user_templates, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'templates': page_obj,
        'page_title': 'My Templates',
        'page_description': 'All your uploaded templates'
    }
    return render(request, 'templates/my_templates.html', context)


def is_admin(user):
    """Check if user is admin or staff"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard for template management"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    difficulty_filter = request.GET.get('difficulty', '')
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-created_at')

    # Base queryset
    templates = Template.objects.select_related('author', 'category').prefetch_related('tags')

    # Apply filters
    if status_filter:
        templates = templates.filter(status=status_filter)

    if category_filter:
        templates = templates.filter(category__slug=category_filter)

    if difficulty_filter:
        templates = templates.filter(difficulty=difficulty_filter)

    if search_query:
        templates = templates.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )

    # Apply sorting
    valid_sorts = [
        'title', '-title', 'created_at', '-created_at',
        'status', '-status', 'download_count', '-download_count',
        'author__username', '-author__username'
    ]
    if sort_by in valid_sorts:
        templates = templates.order_by(sort_by)
    else:
        templates = templates.order_by('-created_at')

    # Pagination
    paginator = Paginator(templates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get statistics
    stats = {
        'total': Template.objects.count(),
        'published': Template.objects.filter(status='published').count(),
        'pending': Template.objects.filter(status='pending').count(),
        'draft': Template.objects.filter(status='draft').count(),
        'rejected': Template.objects.filter(status='rejected').count(),
    }

    # Get categories for filter
    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'templates': page_obj,
        'stats': stats,
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'difficulty_filter': difficulty_filter,
        'search_query': search_query,
        'sort_by': sort_by,
        'difficulty_choices': Template.DIFFICULTY_CHOICES,
        'status_choices': Template.STATUS_CHOICES,
    }
    return render(request, 'templates/admin_dashboard.html', context)


@user_passes_test(is_admin)
@require_POST
def update_template_status(request, pk):
    """Update template status via AJAX"""
    template = get_object_or_404(Template, pk=pk)
    new_status = request.POST.get('status')

    if new_status in dict(Template.STATUS_CHOICES):
        old_status = template.status
        template.status = new_status
        template.save(update_fields=['status'])

        # Log the action
        messages.success(
            request,
            f'Template "{template.title}" status changed from {old_status} to {new_status}'
        )

        return JsonResponse({
            'success': True,
            'message': f'Status updated to {new_status}',
            'new_status': new_status,
            'new_status_display': template.get_status_display()
        })

    return JsonResponse({
        'success': False,
        'message': 'Invalid status'
    })


@user_passes_test(is_admin)
@require_POST
def bulk_template_action(request):
    """Perform bulk actions on templates"""
    template_ids = request.POST.getlist('template_ids')
    action = request.POST.get('action')

    if not template_ids:
        messages.error(request, 'No templates selected')
        return redirect('templates:admin_dashboard')

    templates = Template.objects.filter(pk__in=template_ids)
    count = templates.count()

    if action == 'publish':
        templates.update(status='published')
        messages.success(request, f'{count} template(s) published successfully')
    elif action == 'reject':
        templates.update(status='rejected')
        messages.success(request, f'{count} template(s) rejected')
    elif action == 'pending':
        templates.update(status='pending')
        messages.success(request, f'{count} template(s) set to pending')
    elif action == 'delete':
        template_titles = [t.title for t in templates[:5]]  # Show first 5 titles
        templates.delete()
        titles_str = ', '.join(template_titles)
        if count > 5:
            titles_str += f' and {count - 5} more'
        messages.success(request, f'Deleted templates: {titles_str}')
    else:
        messages.error(request, 'Invalid action')

    return redirect('templates:admin_dashboard')


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

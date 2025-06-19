from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from templates.models import Template
from .models import Review, ReviewHelpful
from .forms import ReviewForm

# Create your views here.

@login_required
def add_review(request, template_id):
    template = get_object_or_404(Template, pk=template_id, status='published')

    # Check if user already reviewed this template
    existing_review = Review.objects.filter(template=template, user=request.user).first()
    if existing_review:
        messages.warning(request, 'You have already reviewed this template.')
        return redirect('templates:template_detail', pk=template.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.template = template
            review.user = request.user
            review.save()

            messages.success(request, 'Your review has been added successfully!')
            return redirect('templates:template_detail', pk=template.pk)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'template': template,
    }
    return render(request, 'reviews/add_review.html', context)


@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your review has been updated successfully!')
            return redirect('templates:template_detail', pk=review.template.pk)
    else:
        form = ReviewForm(instance=review)

    context = {
        'form': form,
        'review': review,
        'template': review.template,
    }
    return render(request, 'reviews/edit_review.html', context)


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    template_pk = review.template.pk

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review has been deleted.')
        return redirect('templates:template_detail', pk=template_pk)

    context = {
        'review': review,
        'template': review.template,
    }
    return render(request, 'reviews/delete_review.html', context)


@login_required
@require_POST
def toggle_helpful(request, review_id):
    """AJAX view to toggle helpful vote on a review"""
    review = get_object_or_404(Review, pk=review_id)

    # Check if user already voted
    helpful_vote, created = ReviewHelpful.objects.get_or_create(
        review=review,
        user=request.user,
        defaults={'is_helpful': True}
    )

    if not created:
        # Toggle the vote
        helpful_vote.is_helpful = not helpful_vote.is_helpful
        helpful_vote.save()

    # Count helpful votes
    helpful_count = review.helpful_votes.filter(is_helpful=True).count()
    not_helpful_count = review.helpful_votes.filter(is_helpful=False).count()

    return JsonResponse({
        'helpful_count': helpful_count,
        'not_helpful_count': not_helpful_count,
        'user_vote': helpful_vote.is_helpful,
    })

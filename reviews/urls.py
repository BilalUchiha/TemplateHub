from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:template_id>/', views.add_review, name='add_review'),
    path('edit/<int:pk>/', views.edit_review, name='edit_review'),
    path('delete/<int:pk>/', views.delete_review, name='delete_review'),
    path('helpful/<int:review_id>/', views.toggle_helpful, name='toggle_helpful'),
]

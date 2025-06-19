from django.urls import path
from . import views

app_name = 'templates'

urlpatterns = [
    path('', views.home, name='home'),
    path('browse/', views.template_list, name='template_list'),
    path('template/<int:pk>/', views.template_detail, name='template_detail'),
    path('upload/', views.template_upload, name='template_upload'),
    path('category/<slug:slug>/', views.category_templates, name='category_templates'),
    path('search/', views.search_templates, name='search_templates'),
    path('download/<int:pk>/', views.download_template, name='download_template'),
    path('favorite/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.user_favorites, name='user_favorites'),
    path('trending/', views.trending_templates, name='trending_templates'),
    path('recent/', views.recent_templates, name='recent_templates'),
    path('compare/', views.compare_templates, name='compare_templates'),
    path('api/template/<int:pk>/', views.template_api, name='template_api'),
    path('my-templates/', views.my_templates, name='my_templates'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/template/<int:pk>/update-status/', views.update_template_status, name='update_template_status'),
    path('admin-dashboard/bulk-action/', views.bulk_template_action, name='bulk_template_action'),
]

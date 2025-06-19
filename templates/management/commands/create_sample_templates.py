from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from templates.models import Template, Category, Tag
from reviews.models import Review
import random


class Command(BaseCommand):
    help = 'Create sample templates for testing'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@templatehub.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()

        # Create additional sample users
        sample_users = []
        for i in range(5):
            user, created = User.objects.get_or_create(
                username=f'user{i+1}',
                defaults={
                    'email': f'user{i+1}@example.com',
                    'first_name': f'User',
                    'last_name': f'{i+1}',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            sample_users.append(user)

        # Get categories
        categories = {
            'html': Category.objects.get(name='HTML Templates'),
            'react': Category.objects.get(name='React Components'),
            'vue': Category.objects.get(name='Vue.js Templates'),
            'django': Category.objects.get(name='Django Apps'),
            'laravel': Category.objects.get(name='Laravel Templates'),
            'angular': Category.objects.get(name='Angular Components'),
        }

        # Get tags
        tags = {
            'responsive': Tag.objects.get(name='responsive'),
            'bootstrap': Tag.objects.get(name='bootstrap'),
            'tailwind': Tag.objects.get(name='tailwind'),
            'dashboard': Tag.objects.get(name='dashboard'),
            'landing': Tag.objects.get(name='landing-page'),
            'ecommerce': Tag.objects.get(name='e-commerce'),
            'blog': Tag.objects.get(name='blog'),
            'portfolio': Tag.objects.get(name='portfolio'),
            'admin': Tag.objects.get(name='admin'),
            'mobile': Tag.objects.get(name='mobile-first'),
            'dark': Tag.objects.get(name='dark-mode'),
            'auth': Tag.objects.get(name='authentication'),
        }

        # Sample templates data
        sample_templates = [
            {
                'title': 'Modern Dashboard Template',
                'category': categories['html'],
                'description': 'A beautiful, responsive dashboard template built with HTML5, CSS3, and JavaScript. Features include charts, tables, forms, and a clean modern design perfect for admin panels and business applications.',
                'short_description': 'Beautiful responsive dashboard template with charts and modern design',
                'difficulty': 'intermediate',
                'tags': [tags['responsive'], tags['dashboard'], tags['admin']],
                'is_featured': True,
                'price': 29.99,
                'is_free': False,
            },
            {
                'title': 'React E-commerce Components',
                'category': categories['react'],
                'description': 'Complete set of React components for building e-commerce applications. Includes product cards, shopping cart, checkout forms, user authentication, and payment integration components.',
                'short_description': 'Complete React component library for e-commerce applications',
                'difficulty': 'advanced',
                'tags': [tags['ecommerce'], tags['responsive'], tags['auth']],
                'is_featured': True,
                'price': 0.00,
                'is_free': True,
            },
            {
                'title': 'Vue.js Blog Template',
                'category': categories['vue'],
                'description': 'A clean and modern blog template built with Vue.js and Tailwind CSS. Features include post listing, single post view, categories, tags, search functionality, and responsive design.',
                'short_description': 'Clean Vue.js blog template with Tailwind CSS styling',
                'difficulty': 'beginner',
                'tags': [tags['blog'], tags['tailwind'], tags['responsive']],
                'is_featured': False,
                'price': 19.99,
                'is_free': False,
            },
            {
                'title': 'Django REST API Starter',
                'category': categories['django'],
                'description': 'Complete Django REST API starter template with user authentication, permissions, serializers, viewsets, and comprehensive documentation. Perfect for building scalable web APIs.',
                'short_description': 'Django REST API starter with authentication and documentation',
                'difficulty': 'advanced',
                'tags': [tags['auth'], tags['admin']],
                'is_featured': True,
                'price': 0.00,
                'is_free': True,
            },
            {
                'title': 'Portfolio Landing Page',
                'category': categories['html'],
                'description': 'Stunning portfolio landing page template perfect for designers, developers, and creative professionals. Features smooth animations, responsive design, and modern layout.',
                'short_description': 'Stunning portfolio landing page with smooth animations',
                'difficulty': 'beginner',
                'tags': [tags['portfolio'], tags['landing'], tags['responsive']],
                'is_featured': False,
                'price': 0.00,
                'is_free': True,
            },
            {
                'title': 'Laravel Admin Panel',
                'category': categories['laravel'],
                'description': 'Complete Laravel admin panel with user management, role-based permissions, CRUD operations, and beautiful UI. Built with Laravel 10 and includes comprehensive documentation.',
                'short_description': 'Complete Laravel admin panel with user management and permissions',
                'difficulty': 'intermediate',
                'tags': [tags['admin'], tags['auth'], tags['dashboard']],
                'is_featured': False,
                'price': 49.99,
                'is_free': False,
            },
            {
                'title': 'Angular Material Dashboard',
                'category': categories['angular'],
                'description': 'Professional Angular dashboard built with Angular Material components. Includes charts, data tables, forms, and a responsive layout perfect for business applications.',
                'short_description': 'Professional Angular dashboard with Material Design components',
                'difficulty': 'intermediate',
                'tags': [tags['dashboard'], tags['admin'], tags['responsive']],
                'is_featured': True,
                'price': 39.99,
                'is_free': False,
            },
            {
                'title': 'Bootstrap 5 Landing Page Kit',
                'category': categories['html'],
                'description': 'Complete Bootstrap 5 landing page kit with multiple layouts, components, and sections. Perfect for startups, agencies, and product launches.',
                'short_description': 'Bootstrap 5 landing page kit with multiple layouts',
                'difficulty': 'beginner',
                'tags': [tags['bootstrap'], tags['landing'], tags['responsive']],
                'is_featured': False,
                'price': 0.00,
                'is_free': True,
            },
            {
                'title': 'React Native Mobile App Template',
                'category': categories['react'],
                'description': 'Complete React Native mobile app template with navigation, authentication, API integration, and beautiful UI components. Perfect for rapid mobile app development.',
                'short_description': 'React Native mobile app template with navigation and auth',
                'difficulty': 'advanced',
                'tags': [tags['mobile'], tags['auth'], tags['responsive']],
                'is_featured': False,
                'price': 59.99,
                'is_free': False,
            },
            {
                'title': 'Dark Mode Portfolio',
                'category': categories['html'],
                'description': 'Modern dark mode portfolio template with smooth animations and responsive design. Features project showcase, about section, and contact form.',
                'short_description': 'Modern dark mode portfolio with smooth animations',
                'difficulty': 'beginner',
                'tags': [tags['dark'], tags['portfolio'], tags['responsive']],
                'is_featured': False,
                'price': 0.00,
                'is_free': True,
            },
        ]

        # Create templates
        created_templates = []
        for template_data in sample_templates:
            template_tags = template_data.pop('tags')
            
            template, created = Template.objects.get_or_create(
                title=template_data['title'],
                defaults={
                    **template_data,
                    'author': random.choice([admin_user] + sample_users),
                    'status': 'published',
                    'download_count': random.randint(10, 500),
                    'version': '1.0.0',
                }
            )
            
            if created:
                template.tags.set(template_tags)
                created_templates.append(template)
                self.stdout.write(f"Created template: {template.title}")

        # Create sample reviews
        review_titles = [
            "Excellent template!",
            "Great quality and documentation",
            "Perfect for my project",
            "Amazing design and functionality",
            "Highly recommended",
            "Good value for money",
            "Easy to customize",
            "Professional quality",
            "Saved me hours of work",
            "Outstanding support"
        ]

        review_comments = [
            "This template exceeded my expectations. The code is clean, well-documented, and easy to customize.",
            "Perfect for my project needs. The design is modern and the functionality is exactly what I was looking for.",
            "Great quality template with excellent documentation. Highly recommended for anyone looking for a professional solution.",
            "Amazing work! The template is responsive, fast, and includes all the features I needed.",
            "Excellent value for money. The template saved me weeks of development time.",
            "Clean code, beautiful design, and great documentation. Everything you need for a successful project.",
            "The template is well-structured and easy to customize. Perfect for both beginners and experienced developers.",
            "Outstanding quality and attention to detail. The author clearly knows what they're doing.",
            "This template is exactly what I was looking for. Professional, modern, and feature-rich.",
            "Highly recommended! The template is well-coded and includes comprehensive documentation."
        ]

        for template in created_templates:
            # Create 2-5 reviews per template
            num_reviews = random.randint(2, 5)
            reviewers = random.sample(sample_users, min(num_reviews, len(sample_users)))
            
            for reviewer in reviewers:
                Review.objects.get_or_create(
                    template=template,
                    user=reviewer,
                    defaults={
                        'rating': random.randint(4, 5),
                        'title': random.choice(review_titles),
                        'comment': random.choice(review_comments),
                        'is_verified_purchase': random.choice([True, False]),
                    }
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(created_templates)} templates with reviews!'
            )
        )

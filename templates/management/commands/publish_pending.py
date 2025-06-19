from django.core.management.base import BaseCommand
from templates.models import Template


class Command(BaseCommand):
    help = 'Publish all pending templates'

    def handle(self, *args, **options):
        pending_templates = Template.objects.filter(status='pending')
        count = pending_templates.count()
        
        if count == 0:
            self.stdout.write(
                self.style.WARNING('No pending templates found.')
            )
            return
        
        # Update all pending templates to published
        pending_templates.update(status='published')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully published {count} template(s)!'
            )
        )
        
        # List the published templates
        for template in pending_templates:
            self.stdout.write(f"  - {template.title} by {template.author.username}")

from django import forms
from django.core.exceptions import ValidationError
from .models import Template, Category, Tag
import zipfile
import os


class TemplateUploadForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select relevant tags for your template"
    )
    
    class Meta:
        model = Template
        fields = [
            'title', 'short_description', 'description', 'category', 'tags',
            'template_file', 'preview_image', 'demo_url', 'difficulty',
            'version', 'is_free', 'price'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'placeholder': 'Enter template title'
            }),
            'short_description': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'placeholder': 'Brief description for listings'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'rows': 6,
                'placeholder': 'Detailed description of your template'
            }),
            'category': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
            }),
            'template_file': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100',
                'accept': '.zip'
            }),
            'preview_image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100',
                'accept': 'image/*'
            }),
            'demo_url': forms.URLInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'placeholder': 'https://example.com/demo'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
            }),
            'version': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'placeholder': '1.0.0'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'step': '0.01',
                'min': '0'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields required
        self.fields['title'].required = True
        self.fields['short_description'].required = True
        self.fields['description'].required = True
        self.fields['category'].required = True
        self.fields['template_file'].required = True
        
        # Set help texts
        self.fields['template_file'].help_text = "Upload a ZIP file containing your template files"
        self.fields['preview_image'].help_text = "Upload a preview image (optional)"
        self.fields['demo_url'].help_text = "Link to live demo (optional)"

    def clean_template_file(self):
        template_file = self.cleaned_data.get('template_file')
        
        if template_file:
            # Check file extension
            if not template_file.name.lower().endswith('.zip'):
                raise ValidationError("Template file must be a ZIP archive.")
            
            # Check file size (max 50MB)
            if template_file.size > 50 * 1024 * 1024:
                raise ValidationError("Template file size cannot exceed 50MB.")
            
            # Validate ZIP file
            try:
                with zipfile.ZipFile(template_file, 'r') as zip_file:
                    # Check if ZIP is valid
                    zip_file.testzip()
                    
                    # Check for minimum required files
                    file_list = zip_file.namelist()
                    if not file_list:
                        raise ValidationError("ZIP file appears to be empty.")
                    
                    # Reset file pointer
                    template_file.seek(0)
                        
            except zipfile.BadZipFile:
                raise ValidationError("Invalid ZIP file.")
            except Exception as e:
                raise ValidationError(f"Error processing ZIP file: {str(e)}")
        
        return template_file

    def clean_preview_image(self):
        preview_image = self.cleaned_data.get('preview_image')
        
        if preview_image:
            # Check file size (max 5MB)
            if preview_image.size > 5 * 1024 * 1024:
                raise ValidationError("Preview image size cannot exceed 5MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if hasattr(preview_image, 'content_type') and preview_image.content_type not in allowed_types:
                raise ValidationError("Preview image must be JPEG, PNG, GIF, or WebP format.")
        
        return preview_image

    def clean(self):
        cleaned_data = super().clean()
        is_free = cleaned_data.get('is_free')
        price = cleaned_data.get('price')
        
        if not is_free and (not price or price <= 0):
            raise ValidationError("Paid templates must have a price greater than 0.")
        
        if is_free and price and price > 0:
            cleaned_data['price'] = 0
        
        return cleaned_data


class TemplateEditForm(TemplateUploadForm):
    """Form for editing existing templates"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make template_file optional for editing
        self.fields['template_file'].required = False
        self.fields['template_file'].help_text = "Upload a new ZIP file to replace the current template (optional)"


class TemplateSearchForm(forms.Form):
    q = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
            'placeholder': 'Search templates...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
        })
    )
    difficulty = forms.ChoiceField(
        choices=[('', 'All Levels')] + Template.DIFFICULTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
        })
    )
    is_free = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'Free'), ('false', 'Paid')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
        })
    )

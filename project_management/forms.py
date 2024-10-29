from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'short_name', 'year']
        widgets = {
            'year': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
        } 
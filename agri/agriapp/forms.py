# forms.py
from django import forms
from .models import Crop

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['name', 'season', 'area']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Wheat, Rice, Potato'
            }),
            'season': forms.Select(attrs={'class': 'form-control'}),
            'area': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Area in acres',
                'step': '0.1',
                'min': '0.1'
            })
        }
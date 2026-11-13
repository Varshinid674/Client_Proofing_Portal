from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Project


# Registration Form
class CustomUserCreationForm(UserCreationForm):

    ROLE_CHOICES = [
        ('agency', 'Agency'),
        ('client', 'Client'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label='Register As',
        widget=forms.Select()
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]


# Project Form
class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project

        fields = [
            'title',
            'description',
            'client_name',
            'client_user',
            'status'
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter project title'
            }),

            'description': forms.Textarea(attrs={
                'placeholder': 'Describe your project',
                'rows': 4
            }),

            'client_name': forms.TextInput(attrs={
                'placeholder': 'Enter client name'
            }),

            'client_user': forms.Select(),

            'status': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['client_user'].queryset = User.objects.all()
        self.fields['client_user'].required = False
        self.fields['client_user'].empty_label = 'Select a client account'
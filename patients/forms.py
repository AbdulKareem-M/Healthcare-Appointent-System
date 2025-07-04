from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Patient

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class LoginForm(forms.Form):
  username = forms.CharField(max_length=30)
  password = forms.CharField(widget=forms.PasswordInput)
  
  
class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['date_of_birth', 'phone', 'address', 'emergency_contact', 'medical_history']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'medical_history': forms.Textarea(attrs={'rows': 4}),
        }
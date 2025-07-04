from django import forms
from .models import Appointment
from django.core.exceptions import ValidationError
from django.utils import timezone

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat()
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'min': '09:00',
                'max': '17:00'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please describe your symptoms or reason for visit...'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise ValidationError("Appointment date cannot be in the past.")
        return date
    
    def clean_time(self):
        time_value = self.cleaned_data.get('time')
        if time_value:
            # Check if time is within working hours (9 AM to 5 PM)
            if time_value < timezone.now().time().replace(hour=9, minute=0) or time_value > timezone.now().time().replace(hour=17, minute=0):
                raise ValidationError("Please select a time between 9:00 AM and 5:00 PM.")
        return time_value
    
    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time_value = cleaned_data.get('time')
        
        if doctor and date and time_value:
            # Check if the doctor already has an appointment at this time
            existing_appointment = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                time=time_value,
                status__in=['scheduled', 'confirmed', 'pending_payment']
            ).exists()
            
            if existing_appointment:
                raise ValidationError("This time slot is already booked. Please choose a different time.")
        
        return cleaned_data


class AppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
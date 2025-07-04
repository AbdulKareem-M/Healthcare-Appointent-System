from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    medical_history = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='patient_profiles/', blank=True, null=True)
    
    def __str__(self):
        return self.user.get_full_name()
    
    def get_absolute_url(self):
        return reverse('patient_detail', args=[str(self.id)])
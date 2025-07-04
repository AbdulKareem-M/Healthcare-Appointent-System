from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Specialty(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Specialties"

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True)
    license_number = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='doctor_profiles/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialty}"
    
    def get_absolute_url(self):
        return reverse('doctor_detail', args=[str(self.id)])
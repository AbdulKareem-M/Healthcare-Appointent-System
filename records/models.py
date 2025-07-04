from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from appointments.models import Appointment
from doctors.models import Doctor
from patients.models import Patient

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    diagnosis = models.TextField()
    treatment = models.TextField()
    prescription = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Medical Record for {self.patient} on {self.date}"
    
    def get_absolute_url(self):
        return reverse('medical_record_detail', args=[str(self.id)])
    
    class Meta:
        ordering = ['-date']
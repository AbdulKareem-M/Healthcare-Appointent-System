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

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('pending_payment', 'Pending Payment'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
        # Payment fields
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)

    
    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date} at {self.time}"
    
    def get_absolute_url(self):
        return reverse('appointment_detail', args=[str(self.id)])
    
    class Meta:
        ordering = ['date', 'time']

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
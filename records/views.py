from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import MedicalRecord
from appointments.models import Appointment
from patients.models import Patient
from doctors.models import Doctor
from .forms import MedicalRecordForm

# Create your views here.
class MedicalRecordListView(LoginRequiredMixin, ListView):
    model = MedicalRecord
    template_name = 'amedical_record_list.html'
    context_object_name = 'records'
    
    def get_queryset(self):
        user = self.request.user
        
        try:
            patient = Patient.objects.get(user=user)
            return MedicalRecord.objects.filter(patient=patient).order_by('-date')
        except Patient.DoesNotExist:
            try:
                doctor = Doctor.objects.get(user=user)
                return MedicalRecord.objects.filter(doctor=doctor).order_by('-date')
            except Doctor.DoesNotExist:
                if user.is_staff:
                    return MedicalRecord.objects.all().order_by('-date')
                return MedicalRecord.objects.none()
            

class MedicalRecordDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = MedicalRecord
    template_name = 'medical_record_detail.html'
    context_object_name = 'record'
    
    def test_func(self):
        record = self.get_object()
        user = self.request.user
        # Check if user is the patient or the doctor for this record
        return (
            hasattr(user, 'patient') and user.patient == record.patient or
            hasattr(user, 'doctor') and user.doctor == record.doctor or
            user.is_staff
        )
        

class MedicalRecordCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'add_medical_record.html'
    
    def test_func(self):
        appointment_id = self.kwargs.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id)
        user = self.request.user
        # Only the doctor of the appointment can create a medical record
        return hasattr(user, 'doctor') and user.doctor == appointment.doctor
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment_id = self.kwargs.get('appointment_id')
        context['appointment'] = get_object_or_404(Appointment, id=appointment_id)
        return context
    
    def form_valid(self, form):
        appointment_id = self.kwargs.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        form.instance.patient = appointment.patient
        form.instance.doctor = appointment.doctor
        form.instance.appointment = appointment
        
        # Update appointment status to completed if not already
        if appointment.status != 'completed':
            appointment.status = 'completed'
            appointment.save()
        
        messages.success(self.request, 'Medical record created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('medical_record_detail', kwargs={'pk': self.object.pk})
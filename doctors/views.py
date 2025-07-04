from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Doctor, Specialty
from appointments.forms import AppointmentForm
from patients.models import Patient
from patients.forms import PatientProfileForm

class DoctorListView(ListView):
    model = Doctor
    template_name = 'doctor_list.html'
    context_object_name = 'doctors'
    
    def get_queryset(self):
        queryset = Doctor.objects.all()
        specialty = self.request.GET.get('specialty')
        search = self.request.GET.get('search')
        
        if specialty:
            queryset = queryset.filter(specialty__name=specialty)
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) | 
                Q(user__last_name__icontains=search) |
                Q(specialty__name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specialties'] = Specialty.objects.all()
        return context


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = 'doctor_detail.html'
    context_object_name = 'doctor'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Only show available appointment slots if user is logged in
        if self.request.user.is_authenticated:
            try:
                patient = Patient.objects.get(user=self.request.user)
                context['is_patient'] = True
                context['appointment_form'] = AppointmentForm(initial={'doctor': self.object})
            except Patient.DoesNotExist:
                context['is_patient'] = False
        return context
    
    
class DoctorProfileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Doctor
    template_name = 'doctor_profile.html'
    context_object_name = 'doctor'
    def test_func(self):
        # Ensure only the doctor can view their own profile
        return self.request.user == self.get_object().user
    def get_object(self):
        return get_object_or_404(Doctor, user=self.request.user)
  
    
class DoctorProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Doctor
    form_class = PatientProfileForm
    template_name = 'edit_profile.html'
    success_url = reverse_lazy('dashboard')
    
    def get_object(self):
        return get_object_or_404(Doctor, user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)
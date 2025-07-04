from django.views.generic import TemplateView, FormView, CreateView, DetailView, UpdateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.core.mail import send_mail
from .forms import UserRegisterForm, LoginForm, PatientProfileForm
from .models import Patient

class RegisterView(TemplateView):
    template_name = 'register.html'
    

class LoginView(FormView):
  form_class = LoginForm
  template_name = 'login.html'
  success_url = reverse_lazy('dashboard')

  def form_valid(self, form):
    user = authenticate(
      username=form.cleaned_data['username'],
      password=form.cleaned_data['password']
    )
    if user is not None:
      login(self.request, user)
      return super().form_valid(form)
    else:
      return self.form_invalid(form)
    

def logout_view(request):
  logout(request)
  return redirect('home')



# Patient Views
class PatientRegistrationView(CreateView):
    template_name = 'register_patient.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        user = form.save()
        patient = Patient.objects.create(user=user)
        send_mail(
            subject='Welcome to Our Healthcare Portal',
            message=f'Hello {user.get_full_name() or user.username},\n\nThank you for registering with us!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        login(self.request, user)
        return redirect('edit_profile')
    
    
class PatientProfileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Patient
    template_name = 'patient_profile.html'
    context_object_name = 'patient'
    
    def test_func(self):
        # Ensure only the patient can view their own profile
        return self.request.user == self.get_object().user
    
    def get_object(self):
        return get_object_or_404(Patient, user=self.request.user)


class PatientProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientProfileForm
    template_name = 'edit_profile.html'
    success_url = reverse_lazy('patient_profile')
    
    def get_object(self):
        return get_object_or_404(Patient, user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)
from django.urls import path
from . import views

urlpatterns = [
  path('register/', views.RegisterView.as_view(), name='register'),
  path('register/patient/', views.PatientRegistrationView.as_view(), name='register_patient'),
  path('login/', views.LoginView.as_view(), name='login'),
  path('logout/', views.logout_view, name='logout'),
  path('profile/', views.PatientProfileView.as_view(), name='patient_profile'),
  path('profile/edit/', views.PatientProfileUpdateView.as_view(), name='edit_profile'),
]
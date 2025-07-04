from django.urls import path
from . import views
from .views import DoctorProfileView, DoctorProfileUpdateView

urlpatterns = [
    # Home and authentication
    path('', views.HomeView.as_view(), name='home'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register/patient/', views.PatientRegistrationView.as_view(), name='register_patient'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Doctor views
    path('doctors/', views.DoctorListView.as_view(), name='doctor_list'),
    path('doctors/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    path('doctors/<int:pk>/profile/', DoctorProfileView.as_view(), name='doctor_profile'),
    path('doctors/<int:pk>/edit-profile/', DoctorProfileUpdateView.as_view(), name='edit_doctor_profile'),
    
    # Patient views
    path('profile/', views.PatientProfileView.as_view(), name='patient_profile'),
    path('profile/edit/', views.PatientProfileUpdateView.as_view(), name='edit_profile'),
    
    # Appointment views
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/new/', views.AppointmentCreateView.as_view(), name='new_appointment'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='edit_appointment'),
    path('appointment/<int:pk>/cancel/', views.EnhancedAppointmentCancelView.as_view(), name='cancel_appointment_with_refund'),
    
    # Medical records
    path('medical-records/', views.MedicalRecordListView.as_view(), name='medical_record_list'),
    path('medical-records/<int:pk>/', views.MedicalRecordDetailView.as_view(), name='medical_record_detail'),
    path('appointments/<int:appointment_id>/add-record/', views.MedicalRecordCreateView.as_view(), name='add_medical_record'),
    
    # payment views
    path('payment/<int:appointment_id>/', views.PaymentView.as_view(), name='payment_page'),
    path('payment/failed/<int:appointment_id>/', views.PaymentFailedView.as_view(), name='payment_failed'),
    path('webhook/razorpay/', views.razorpay_webhook, name='razorpay_webhook'),
    path('payment/callback/', views.EnhancedPaymentCallbackView.as_view(), name='payment_callback'),
    


]
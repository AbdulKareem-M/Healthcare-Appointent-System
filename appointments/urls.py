from django.urls import path
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.HomeView.as_view(), name='home'),
    
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Patient views
    
    
    # Appointment views
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/new/', views.AppointmentCreateView.as_view(), name='new_appointment'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='edit_appointment'),
    path('appointment/<int:pk>/cancel/', views.EnhancedAppointmentCancelView.as_view(), name='cancel_appointment_with_refund'),
    
    # Medical records
    
    
    # payment views
    path('payment/<int:appointment_id>/', views.PaymentView.as_view(), name='payment_page'),
    path('payment/failed/<int:appointment_id>/', views.PaymentFailedView.as_view(), name='payment_failed'),
    path('webhook/razorpay/', views.razorpay_webhook, name='razorpay_webhook'),
    path('payment/callback/', views.EnhancedPaymentCallbackView.as_view(), name='payment_callback'),
    


]
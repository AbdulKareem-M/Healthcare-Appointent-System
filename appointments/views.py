from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    TemplateView, ListView, DetailView, 
    CreateView, UpdateView
)
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.mail import send_mail
from django.utils.html import strip_tags
import logging
import json

from .models import Appointment
from patients.models import Patient
from doctors.models import Doctor, Specialty
from records.models import MedicalRecord
from records.forms import MedicalRecordForm
from .forms import AppointmentForm, AppointmentUpdateForm
from .utils.payment import (
    create_payment_order, verify_payment_signature, 
    create_razorpay_client, send_payment_confirmation_email
)

from datetime import datetime, timedelta
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


# Home and Authentication Views
class HomeView(TemplateView):
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specialties'] = Specialty.objects.all()[:6]
        context['doctors'] = Doctor.objects.all()[:4]
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            patient = Patient.objects.get(user=user)
            context['patient'] = patient
            context['upcoming_appointments'] = Appointment.objects.filter(
                patient=patient, 
                status__in=['scheduled', 'confirmed']
            ).order_by('date', 'time')[:5]
            context['recent_appointments'] = Appointment.objects.filter(
                patient=patient, 
                status__in=['completed']
            ).order_by('-date', '-time')[:5]
            context['medical_records'] = MedicalRecord.objects.filter(
                patient=patient
            ).order_by('-date')[:5]
        except Patient.DoesNotExist:
            # Handle case where user is not a patient (could be doctor or admin)
            try:
                doctor = Doctor.objects.get(user=user)
                context['doctor'] = doctor
                context['today_appointments'] = Appointment.objects.filter(
                    doctor=doctor,
                    date=timezone.now().date(),
                    status__in=['scheduled', 'confirmed']
                ).order_by('time')
                context['upcoming_appointments'] = Appointment.objects.filter(
                    doctor=doctor,
                    date__gt=timezone.now().date(),
                    status__in=['scheduled', 'confirmed']
                ).order_by('date', 'time')[:10]
            except Doctor.DoesNotExist:
                # User is neither patient nor doctor (admin)
                pass
        
        return context


# Appointment Views

class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/new_appointment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doctors'] = Doctor.objects.select_related('user', 'specialty').all()
        context['razorpay_key_id'] = settings.RAZORPAY_KEY_ID
        return context
    
    def form_valid(self, form):
        try:
            patient = Patient.objects.get(user=self.request.user)
            form.instance.patient = patient
            form.instance.status = 'pending_payment'
            
            # Save appointment first
            appointment = form.save()
            
            
            # Create Razorpay order
            order = create_payment_order(
                amount=float(appointment.consultation_fee),
                receipt=f'appointment_{appointment.id}'
            )
            
            if order:
                appointment.razorpay_order_id = order['id']
                appointment.save()
                
                # Redirect to payment page
                return redirect('payment_page', appointment_id=appointment.id)
            else:
                messages.error(self.request, 'Payment order creation failed. Please try again.')
                appointment.delete()  # Clean up
                return self.form_invalid(form)
                
        except Patient.DoesNotExist:
            messages.error(self.request, 'You must be registered as a patient to book appointments.')
            return redirect('dashboard')
        

class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/appointment_list.html'
    context_object_name = 'appointments'
    
    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.GET.get('status', 'upcoming')
        
        try:
            patient = Patient.objects.get(user=user)
            queryset = Appointment.objects.filter(patient=patient)
            
            if status_filter == 'upcoming':
                queryset = queryset.filter(status__in=['scheduled', 'confirmed']).order_by('date', 'time')
            elif status_filter == 'past':
                queryset = queryset.filter(status__in=['completed', 'cancelled', 'no_show']).order_by('-date', '-time')
            elif status_filter == 'all':
                queryset = queryset.order_by('-date', '-time')
            
            return queryset
        except Patient.DoesNotExist:
            try:
                doctor = Doctor.objects.get(user=user)
                queryset = Appointment.objects.filter(doctor=doctor)
                
                if status_filter == 'upcoming':
                    queryset = queryset.filter(status__in=['scheduled', 'confirmed']).order_by('date', 'time')
                elif status_filter == 'past':
                    queryset = queryset.filter(status__in=['completed', 'cancelled', 'no_show']).order_by('-date', '-time')
                elif status_filter == 'all':
                    queryset = queryset.order_by('-date', '-time')
                
                return queryset
            except Doctor.DoesNotExist:
                return Appointment.objects.none()



class AppointmentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Appointment
    template_name = 'appointments/appointment_detail.html'
    context_object_name = 'appointment'
    
    def test_func(self):
        appointment = self.get_object()
        user = self.request.user
        # Check if user is the patient or the doctor for this appointment
        return (
            hasattr(user, 'patient') and user.patient == appointment.patient or
            hasattr(user, 'doctor') and user.doctor == appointment.doctor or
            user.is_staff
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment = self.get_object()
        
        # Check if there's a medical record for this appointment
        try:
            medical_record = MedicalRecord.objects.get(appointment=appointment)
            context['medical_record'] = medical_record
        except MedicalRecord.DoesNotExist:
            context['medical_record'] = None
        
        # Add update form for doctors
        if hasattr(self.request.user, 'doctor') and self.request.user.doctor == appointment.doctor:
            context['update_form'] = AppointmentUpdateForm(instance=appointment)
            
            # Add medical record form if appointment is completed and no record exists
            if appointment.status == 'completed' and not context['medical_record']:
                context['medical_record_form'] = MedicalRecordForm()
        
        return context

class AppointmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Appointment
    form_class = AppointmentUpdateForm
    template_name = 'appointments/edit_appointment.html'
    
    def test_func(self):
        appointment = self.get_object()
        user = self.request.user
        # Only doctors can update appointment details
        return hasattr(user, 'doctor') and user.doctor == appointment.doctor
    
    def get_success_url(self):
        return reverse('appointment_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Appointment updated successfully!')
        return super().form_valid(form)


class EnhancedAppointmentCancelView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Appointment
    fields = []
    template_name = 'appointments/cancel_appointment.html'
    success_url = reverse_lazy('appointment_list')

    def test_func(self):
        appointment = self.get_object()
        user = self.request.user
        return (
            hasattr(user, 'patient') and user.patient == appointment.patient and
            appointment.status in ['scheduled', 'confirmed']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment = self.get_object()
        appointment_datetime = datetime.combine(appointment.date, appointment.time)
        cancellation_deadline = appointment_datetime - timedelta(hours=24)
        
        context['appointment'] = appointment
        context['refund_eligible'] = datetime.now() <= cancellation_deadline
        context['refund_amount'] = appointment.consultation_fee if context['refund_eligible'] else 0
        return context

    def post(self, request, *args, **kwargs):
        appointment = self.get_object()
        appointment_datetime = datetime.combine(appointment.date, appointment.time)
        cancellation_deadline = appointment_datetime - timedelta(hours=24)
        refund_eligible = datetime.now() <= cancellation_deadline

        if refund_eligible and appointment.payment_status == 'paid':
            success, message = process_refund(appointment, "Patient cancelled appointment")
            if success:
                messages.success(self.request, f'Appointment cancelled successfully! Refund of ₹{appointment.consultation_fee} will be processed within 5-7 business days.')
            else:
                messages.warning(self.request, f'Appointment cancelled but refund failed: {message}. Please contact support.')
        else:
            if refund_eligible:
                messages.success(self.request, 'Appointment cancelled successfully!')
            else:
                messages.warning(self.request, 'Appointment cancelled. No refund available due to late cancellation.')

        # ✅ This now works as expected
        appointment.status = 'cancelled'
        appointment.save()
        return redirect(self.success_url)


# payment views
class PaymentView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment_id = self.kwargs['appointment_id']
        
        try:
            appointment = get_object_or_404(
                Appointment, 
                id=appointment_id, 
                patient__user=self.request.user,
                status='pending_payment'
            )
            
            context.update({
                'appointment': appointment,
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': int(appointment.consultation_fee * 100),  # Amount in paise
                'currency': 'INR',
                'order_id': appointment.razorpay_order_id,
                'user_name': f"{self.request.user.first_name} {self.request.user.last_name}",
                'user_email': self.request.user.email,
                'user_phone': getattr(appointment.patient, 'phone', ''),
            })
            
        except Appointment.DoesNotExist:
            messages.error(self.request, 'Invalid appointment or payment already completed.')
            return redirect('appointment_list')
            
        return context



class PaymentFailedView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payment_failed.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment_id = self.kwargs['appointment_id']
        
        try:
            appointment = get_object_or_404(
                Appointment, 
                id=appointment_id, 
                patient__user=self.request.user
            )
            context['appointment'] = appointment
        except Appointment.DoesNotExist:
            pass
            
        return context
    
    
# Add webhook for payment verification 
@csrf_exempt
def razorpay_webhook(request):
    if request.method == 'POST':
        try:
            # Verify webhook signature
            webhook_signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE')
            webhook_body = request.body
            
            # Verify webhook (implement according to Razorpay docs)
            
            # Process webhook data
            webhook_data = json.loads(webhook_body)
            event = webhook_data.get('event')
            
            if event == 'payment.captured':
                payment_entity = webhook_data['payload']['payment']['entity']
                order_id = payment_entity.get('order_id')
                
                try:
                    appointment = Appointment.objects.get(razorpay_order_id=order_id)
                    if appointment.payment_status != 'paid':
                        appointment.payment_status = 'paid'
                        appointment.status = 'scheduled'
                        appointment.save()
                except Appointment.DoesNotExist:
                    pass
            
            return JsonResponse({'status': 'ok'})
            
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return HttpResponseBadRequest('Invalid webhook')
    
    return HttpResponseBadRequest('Method not allowed')



def send_payment_confirmation_email(appointment):
    """Send payment confirmation email to patient"""
    try:
        subject = 'Payment Confirmation - Appointment Booked'

        context = {
            'patient_name': f"{appointment.patient.user.first_name} {appointment.patient.user.last_name}",
            'doctor_name': f"{appointment.doctor.user.first_name} {appointment.doctor.user.last_name}",
            'specialty': appointment.doctor.specialty.name,
            'appointment_date': appointment.date.strftime('%B %d, %Y'),
            'appointment_time': appointment.time.strftime('%I:%M %p'),
            'amount': appointment.consultation_fee,
            'payment_id': appointment.razorpay_payment_id,
        }

        # Correctly render the HTML template with context
        html_message = render_to_string('emails/payment_success.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


logger = logging.getLogger(__name__)


class EnhancedPaymentCallbackView(TemplateView):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        try:
            # Get payment details from request
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_signature = request.POST.get('razorpay_signature')
            
            # Find appointment
            appointment = get_object_or_404(
                Appointment, 
                razorpay_order_id=razorpay_order_id
            )
            
            # Verify signature
            if verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
                # Payment successful
                appointment.payment_status = 'paid'
                appointment.status = 'scheduled'
                appointment.razorpay_payment_id = razorpay_payment_id
                appointment.razorpay_signature = razorpay_signature
                appointment.save()
                
                # Send confirmation email
                send_payment_confirmation_email(appointment)
                
                messages.success(request, 'Payment successful! Your appointment has been confirmed. A confirmation email has been sent.')
                return redirect('appointment_detail', pk=appointment.id)
            else:
                # Payment verification failed
                appointment.payment_status = 'failed'
                appointment.save()
                messages.error(request, 'Payment verification failed. Please contact support.')
                return redirect('payment_failed', appointment_id=appointment.id)
                
        except Exception as e:
            logger.error(f"Payment callback error: {e}")
            messages.error(request, 'Payment processing error. Please contact support.')
            return redirect('dashboard')


# 7. Add refund functionality
def process_refund(appointment, reason="Appointment cancelled"):
    """Process refund for cancelled appointments"""
    try:
        if appointment.payment_status != 'paid' or not appointment.razorpay_payment_id:
            return False, "No valid payment found for refund"
        
        client = create_razorpay_client()
        
        # Create refund
        refund_data = {
            'amount': int(appointment.consultation_fee * 100),  # Amount in paise
            'notes': {
                'reason': reason,
                'appointment_id': str(appointment.id)
            }
        }
        
        refund = client.payment.refund(appointment.razorpay_payment_id, refund_data)
        
        if refund['status'] == 'processed':
            appointment.payment_status = 'refunded'
            appointment.status = 'cancelled'
            appointment.save()
            return True, "Refund processed successfully"
        else:
            return False, "Refund initiation failed"
            
    except Exception as e:
        logger.error(f"Refund error: {e}")
        return False, f"Refund error: {str(e)}"

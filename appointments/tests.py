from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Doctor, Patient, Appointment, Specialty, MedicalRecord

class AppointmentModelTests(TestCase):
    def setUp(self):
        # Create a specialty
        self.specialty = Specialty.objects.create(
            name="Cardiology",
            description="Heart related issues"
        )
        
        # Create users for doctor and patient
        self.doctor_user = User.objects.create_user(
            username='doctor1',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.patient_user = User.objects.create_user(
            username='patient1',
            password='testpass123',
            first_name='Jane',
            last_name='Smith'
        )
        
        # Create doctor and patient profiles
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialty=self.specialty,
            license_number='MED12345',
            phone='555-123-4567'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth='1990-01-01',
            phone='555-987-6543',
            address='123 Main St'
        )
        
        # Create an appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date='2025-01-01',
            time='14:30:00',
            reason='Annual checkup',
            status='scheduled'
        )

    def test_appointment_creation(self):
        self.assertEqual(self.appointment.patient.user.first_name, 'Jane')
        self.assertEqual(self.appointment.doctor.user.first_name, 'John')
        self.assertEqual(self.appointment.status, 'scheduled')

    def test_doctor_string_representation(self):
        self.assertEqual(str(self.doctor), 'Dr. John Doe')

    def test_patient_string_representation(self):
        self.assertEqual(str(self.patient), 'Jane Smith')

    def test_appointment_string_representation(self):
        self.assertEqual(
            str(self.appointment),
            f"{self.patient} with {self.doctor} on {self.appointment.date} at {self.appointment.time}"
        )
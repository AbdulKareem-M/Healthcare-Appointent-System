from django.contrib import admin
from .models import Doctor, Patient, Appointment, Specialty, MedicalRecord

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'license_number', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialty__name')
    list_filter = ('specialty',)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'phone', 'emergency_contact')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status')
    list_filter = ('status', 'date', 'doctor')
    search_fields = ('patient__user__username', 'doctor__user__username')
    date_hierarchy = 'date'

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'diagnosis')
    list_filter = ('date', 'doctor')
    search_fields = ('patient__user__username', 'doctor__user__username', 'diagnosis')
    date_hierarchy = 'date'
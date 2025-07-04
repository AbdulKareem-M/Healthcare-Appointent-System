from django.contrib import admin
from .models import MedicalRecord

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'diagnosis')
    list_filter = ('date', 'doctor')
    search_fields = ('patient__user__username', 'doctor__user__username', 'diagnosis')
    date_hierarchy = 'date'

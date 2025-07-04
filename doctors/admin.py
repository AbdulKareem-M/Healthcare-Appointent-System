from django.contrib import admin
from .models import Doctor, Specialty

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'license_number', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialty__name')
    list_filter = ('specialty',)
    
@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
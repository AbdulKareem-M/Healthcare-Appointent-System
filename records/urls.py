from django.urls import path
from . import views

urlpatterns = [
  path('medical-records/', views.MedicalRecordListView.as_view(), name='medical_record_list'),
  path('medical-records/<int:pk>/', views.MedicalRecordDetailView.as_view(), name='medical_record_detail'),
  path('appointments/<int:appointment_id>/add-record/', views.MedicalRecordCreateView.as_view(), name='add_medical_record'),
]
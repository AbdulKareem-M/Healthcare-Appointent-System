from django.urls import path
from . import views

urlpatterns = [
  path('doctors/', views.DoctorListView.as_view(), name='doctor_list'),
  path('doctors/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
  path('doctors/<int:pk>/profile/', views.DoctorProfileView.as_view(), name='doctor_profile'),
  path('doctors/<int:pk>/edit-profile/', views.DoctorProfileUpdateView.as_view(), name='edit_doctor_profile'),
]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("custom-admin/", views.custom_admin_dashboard, name="custom_admin_dashboard"),
    path("patient-dashboard/", views.patient_dashboard, name="patient_dashboard"),
    path("doctor-dashboard/", views.doctor_dashboard, name="doctor_dashboard"),
    path("doctor/add-slot/", views.add_doctor_slot, name="add_doctor_slot"),

    path("hospitals/", views.hospital_list, name="hospital_list"),
    path("hospitals/<int:hospital_id>/doctors/", views.doctors_by_hospital, name="doctors_by_hospital"),
    path("doctors/<int:doctor_id>/slots/", views.doctor_slots, name="doctor_slots"),

    path("book-slot/<int:slot_id>/", views.book_slot, name="book_slot"),
    path("appointment-confirmation/<int:appointment_id>/", views.appointment_confirmation, name="appointment_confirmation"),
    path("cancel-appointment/<int:appointment_id>/", views.cancel_appointment, name="cancel_appointment"),

    path("patient-history/<int:patient_id>/", views.patient_history_detail, name="patient_history_detail"),
    path("prescription/<int:prescription_id>/pdf/", views.prescription_pdf, name="prescription_pdf"),
]
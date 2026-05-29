from django.contrib import admin
from .models import DoctorSlot, Appointment, MedicalHistory, Prescription, MedicalDocument


@admin.register(DoctorSlot)
class DoctorSlotAdmin(admin.ModelAdmin):
    list_display = ("doctor", "date", "start_time", "end_time", "is_booked")
    list_filter = ("is_booked", "date", "doctor")
    search_fields = ("doctor__user__username", "doctor__specialization")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "appointment_date", "appointment_time", "fees", "status")
    list_filter = ("status", "appointment_date", "doctor")
    search_fields = ("patient__user__username", "doctor__user__username")


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ("patient", "last_updated")
    search_fields = ("patient__user__username", "disease_history", "allergies", "diagnosis")


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "medicine_name", "dosage", "frequency", "duration", "created_at")
    list_filter = ("doctor", "created_at")
    search_fields = ("patient__user__username", "doctor__user__username", "medicine_name", "diagnosis")

@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ("patient", "title", "document_type", "uploaded_at")
    list_filter = ("document_type", "uploaded_at")
    search_fields = ("patient__user__username", "title", "document_type")
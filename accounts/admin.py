from django.contrib import admin
from .models import PatientProfile, DoctorProfile
from .models import PatientProfile, DoctorProfile, Hospital

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "phone", "email")
    search_fields = ("name", "city", "phone", "email")
    list_filter = ("city",)


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "age", "gender", "blood_group")
    search_fields = ("user__username", "user__email", "phone")


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "hospital",
        "phone",
        "specialization",
        "qualification",
        "experience",
        "consultation_fees",
    )
    list_filter = ("hospital", "specialization", "qualification")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "hospital__name",
        "phone",
        "specialization",
    )
    ordering = ("id",)
    
    search_fields = ("user__username", "user__email", "specialization")
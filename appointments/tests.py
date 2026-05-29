from django.db import models
from accounts.models import PatientProfile, DoctorProfile


class DoctorSlot(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.doctor} - {self.date} - {self.start_time}"


class Appointment(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    slot = models.OneToOneField(DoctorSlot, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    fees = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, default="Confirmed")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} with {self.doctor}"


class MedicalHistory(models.Model):
    patient = models.OneToOneField(PatientProfile, on_delete=models.CASCADE)
    disease_history = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    previous_surgeries = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Medical History - {self.patient}"
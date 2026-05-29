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

    disease_history = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)
    previous_surgeries = models.TextField(blank=True, null=True)

    diagnosis = models.TextField(blank=True, null=True)
    lab_result_summary = models.TextField(blank=True, null=True)
    prescription_summary = models.TextField(blank=True, null=True)
    doctor_notes = models.TextField(blank=True, null=True)

    notes = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Medical History - {self.patient.user.username}"
    
class Prescription(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)

    diagnosis = models.TextField(blank=True, null=True)
    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    duration = models.CharField(max_length=255)
    instructions = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient.user.username} by Dr. {self.doctor.user.username}"

class MedicalDocument(models.Model):
    DOCUMENT_TYPES = [
        ("Lab Report", "Lab Report"),
        ("Prescription", "Prescription"),
        ("Discharge Summary", "Discharge Summary"),
        ("X-Ray", "X-Ray"),
        ("MRI", "MRI"),
        ("CT Scan", "CT Scan"),
        ("Blood Test", "Blood Test"),
        ("Other", "Other"),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=100, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to="medical_documents/")
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.patient.user.username}"
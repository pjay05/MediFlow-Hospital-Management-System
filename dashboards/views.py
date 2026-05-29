from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date

from accounts.models import DoctorProfile, PatientProfile, Hospital
from appointments.models import DoctorSlot, Appointment, MedicalHistory, Prescription, MedicalDocument
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

def home(request):
    return render(request, "home.html")


@login_required
def custom_admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("home")

    total_doctors = DoctorProfile.objects.count()
    total_patients = PatientProfile.objects.count()
    total_slots = DoctorSlot.objects.count()
    total_appointments = Appointment.objects.count()

    recent_slots = DoctorSlot.objects.select_related("doctor").order_by("-date")[:5]
    recent_appointments = Appointment.objects.select_related("patient", "doctor").order_by("-created_at")[:5]

    context = {
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_slots": total_slots,
        "total_appointments": total_appointments,
        "recent_slots": recent_slots,
        "recent_appointments": recent_appointments,
    }

    return render(request, "custom_admin_dashboard.html", context)


@login_required
def patient_dashboard(request):
    try:
        patient = PatientProfile.objects.get(user=request.user)
    except PatientProfile.DoesNotExist:
        return redirect("home")

    today = date.today()

    available_slots = DoctorSlot.objects.filter(
        is_booked=False
    ).select_related("doctor", "doctor__hospital").order_by("date", "start_time")

    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date__gte=today
    ).select_related("doctor", "slot").order_by("appointment_date", "appointment_time")

    past_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date__lt=today
    ).select_related("doctor", "slot").order_by("-appointment_date", "-appointment_time")

    medical_history, created = MedicalHistory.objects.get_or_create(patient=patient)
    documents = MedicalDocument.objects.filter(patient=patient).order_by("-uploaded_at")
    context = {
        "patient": patient,
        "available_slots": available_slots,
        "appointments": upcoming_appointments,
        "past_appointments": past_appointments,
        "medical_history": medical_history,
    }

    return render(request, "patient_dashboard.html", context)


@login_required
def doctor_dashboard(request):
    try:
        doctor = DoctorProfile.objects.get(user=request.user)
    except DoctorProfile.DoesNotExist:
        return redirect("home")

    slots = DoctorSlot.objects.filter(doctor=doctor).order_by("-date")
    appointments = Appointment.objects.filter(doctor=doctor).select_related("patient", "slot")

    context = {
        "doctor": doctor,
        "slots": slots,
        "appointments": appointments,
    }

    return render(request, "doctor_dashboard.html", context)

@login_required
def book_slot(request, slot_id):
    try:
        patient = PatientProfile.objects.get(user=request.user)
    except PatientProfile.DoesNotExist:
        return redirect("home")

    slot = get_object_or_404(DoctorSlot, id=slot_id)

    # If slot is already booked, do not create duplicate appointment
    existing_appointment = Appointment.objects.filter(slot=slot).first()

    if existing_appointment:
        messages.success(request, "Appointment booked successfully.")
        return redirect("appointment_confirmation", appointment_id=existing_appointment.id)

    if slot.is_booked:
      messages.warning(request, "This slot is already booked. Please choose another slot.")
      return redirect("patient_dashboard")

    appointment = Appointment.objects.create(
        patient=patient,
        doctor=slot.doctor,
        slot=slot,
        appointment_date=slot.date,
        appointment_time=slot.start_time,
        fees=slot.doctor.consultation_fees,
        status="Confirmed"
    )

    slot.is_booked = True
    slot.save()
    
@login_required
def patient_history_detail(request, patient_id):
    patient = get_object_or_404(PatientProfile, id=patient_id)

    medical_history, created = MedicalHistory.objects.get_or_create(patient=patient)

    appointments = Appointment.objects.filter(
        patient=patient
    ).select_related("doctor").order_by("-appointment_date", "-appointment_time")
    prescriptions = Prescription.objects.filter(
    patient=patient
    ).select_related("doctor").order_by("-created_at")

    prescriptions = Prescription.objects.filter(
    patient=patient
    ).select_related("doctor").order_by("-created_at")

    documents = MedicalDocument.objects.filter(patient=patient).order_by("-uploaded_at")

    if request.method == "POST":
        medical_history.disease_history = request.POST.get("disease_history")
        medical_history.allergies = request.POST.get("allergies")
        medical_history.current_medications = request.POST.get("current_medications")
        medical_history.previous_surgeries = request.POST.get("previous_surgeries")
        medical_history.diagnosis = request.POST.get("diagnosis")
        medical_history.lab_result_summary = request.POST.get("lab_result_summary")
        medical_history.prescription_summary = request.POST.get("prescription_summary")
        medical_history.doctor_notes = request.POST.get("doctor_notes")
        medical_history.notes = request.POST.get("notes")

        medical_history.save()
        

        medicine_name = request.POST.get("medicine_name")
        dosage = request.POST.get("dosage")
        frequency = request.POST.get("frequency")
        duration = request.POST.get("duration")
        prescription_instructions = request.POST.get("prescription_instructions")

        if medicine_name and dosage and frequency and duration:
            doctor = DoctorProfile.objects.get(user=request.user)

            latest_appointment = Appointment.objects.filter(
                patient=patient,
                doctor=doctor
            ).order_by("-appointment_date", "-appointment_time").first()

            Prescription.objects.create(
                patient=patient,
                doctor=doctor,
                appointment=latest_appointment,
                diagnosis=medical_history.diagnosis,
                medicine_name=medicine_name,
                dosage=dosage,
                frequency=frequency,
                duration=duration,
                documents=documents,
                instructions=prescription_instructions
            )

        messages.success(request, "Patient EHR updated successfully.")
        return redirect("patient_history_detail", patient_id=patient.id)

    context = {
        "patient": patient,
        "medical_history": medical_history,
        "appointments": appointments,
        "prescriptions": prescriptions,
    }

    return render(request, "patient_history_detail.html", context)
    

@login_required
def hospital_list(request):
    try:
        PatientProfile.objects.get(user=request.user)
    except PatientProfile.DoesNotExist:
        return redirect("home")

    hospitals = Hospital.objects.all().order_by("name")

    context = {
        "hospitals": hospitals,
    }

    return render(request, "hospital_list.html", context)


@login_required
def doctors_by_hospital(request, hospital_id):
    try:
        PatientProfile.objects.get(user=request.user)
    except PatientProfile.DoesNotExist:
        return redirect("home")

    hospital = get_object_or_404(Hospital, id=hospital_id)
    doctors = DoctorProfile.objects.filter(hospital=hospital).order_by("specialization")

    context = {
        "hospital": hospital,
        "doctors": doctors,
    }

    return render(request, "doctors_by_hospital.html", context)


@login_required
def add_doctor_slot(request):
    try:
        doctor = DoctorProfile.objects.get(user=request.user)
    except DoctorProfile.DoesNotExist:
        messages.error(request, "Only doctors can add appointment slots.")
        return redirect("home")

    if request.method == "POST":
        date = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        if not date or not start_time or not end_time:
            messages.error(request, "Please fill all slot fields.")
            return redirect("doctor_dashboard")

        if start_time >= end_time:
            messages.error(request, "End time must be after start time.")
            return redirect("doctor_dashboard")

        duplicate_slot = DoctorSlot.objects.filter(
            doctor=doctor,
            date=date,
            start_time=start_time,
            end_time=end_time
        ).exists()

        if duplicate_slot:
            messages.warning(request, "This slot already exists.")
            return redirect("doctor_dashboard")

        DoctorSlot.objects.create(
            doctor=doctor,
            date=date,
            start_time=start_time,
            end_time=end_time,
            is_booked=False
        )

        messages.success(request, "New appointment slot added successfully.")
        return redirect("doctor_dashboard")

    return redirect("doctor_dashboard")


@login_required
def appointment_confirmation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    context = {
        "appointment": appointment,
    }

    return render(request, "appointment_confirmation.html", context)

@login_required
def doctor_slots(request, doctor_id):
    try:
        PatientProfile.objects.get(user=request.user)
    except PatientProfile.DoesNotExist:
        return redirect("home")

    doctor = get_object_or_404(DoctorProfile, id=doctor_id)

    available_slots = DoctorSlot.objects.filter(
        doctor=doctor,
        is_booked=False
    ).order_by("date", "start_time")

    context = {
        "doctor": doctor,
        "available_slots": available_slots,
    }

    return render(request, "doctor_slots.html", context)

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Only the same patient can cancel their own appointment
    try:
        patient = PatientProfile.objects.get(user=request.user)
    except PatientProfile.DoesNotExist:
        messages.error(request, "Only patients can cancel appointments.")
        return redirect("home")

    if appointment.patient != patient:
        messages.error(request, "You are not allowed to cancel this appointment.")
        return redirect("patient_dashboard")

    if appointment.status == "Cancelled":
        messages.warning(request, "This appointment is already cancelled.")
        return redirect("patient_dashboard")

    appointment.status = "Cancelled"
    appointment.save()

    # Make the doctor slot available again
    if appointment.slot:
        appointment.slot.is_booked = False
        appointment.slot.save()

    messages.success(request, "Appointment cancelled successfully.")
    return redirect("patient_dashboard")

@login_required
def prescription_pdf(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="prescription_{prescription.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 60

    # Header
    p.setFont("Helvetica-Bold", 22)
    p.drawString(60, y, "MediFlow Hospital")
    y -= 25

    p.setFont("Helvetica", 11)
    p.drawString(60, y, "Digital Prescription")
    y -= 35

    # Prescription ID
    p.setFont("Helvetica-Bold", 12)
    p.drawString(60, y, f"Prescription ID: MEDI-RX-{prescription.id}")
    y -= 25

    # Patient and doctor details
    p.setFont("Helvetica-Bold", 13)
    p.drawString(60, y, "Patient Details")
    y -= 20

    p.setFont("Helvetica", 11)
    p.drawString(60, y, f"Patient: {prescription.patient.user.username}")
    y -= 18
    p.drawString(60, y, f"Age: {prescription.patient.age}")
    y -= 18
    p.drawString(60, y, f"Gender: {prescription.patient.gender}")
    y -= 18
    p.drawString(60, y, f"Blood Group: {prescription.patient.blood_group}")
    y -= 30

    p.setFont("Helvetica-Bold", 13)
    p.drawString(60, y, "Doctor Details")
    y -= 20

    p.setFont("Helvetica", 11)
    p.drawString(60, y, f"Doctor: Dr. {prescription.doctor.user.username}")
    y -= 18
    p.drawString(60, y, f"Specialization: {prescription.doctor.specialization}")
    y -= 18
    p.drawString(60, y, f"Qualification: {prescription.doctor.qualification}")
    y -= 30

    # Prescription details
    p.setFont("Helvetica-Bold", 13)
    p.drawString(60, y, "Prescription")
    y -= 22

    p.setFont("Helvetica", 11)
    p.drawString(60, y, f"Diagnosis: {prescription.diagnosis or 'Not added'}")
    y -= 22
    p.drawString(60, y, f"Medicine: {prescription.medicine_name}")
    y -= 18
    p.drawString(60, y, f"Dosage: {prescription.dosage}")
    y -= 18
    p.drawString(60, y, f"Frequency: {prescription.frequency}")
    y -= 18
    p.drawString(60, y, f"Duration: {prescription.duration}")
    y -= 22

    p.drawString(60, y, "Instructions:")
    y -= 18

    instructions = prescription.instructions or "No special instructions."
    text_object = p.beginText(80, y)
    text_object.setFont("Helvetica", 11)

    for line in instructions.split("\n"):
        text_object.textLine(line)

    p.drawText(text_object)

    # Footer
    p.setFont("Helvetica", 9)
    p.drawString(60, 60, "This is a digitally generated prescription from MediFlow.")
    p.drawString(60, 45, "Please consult your doctor before making any medication changes.")

    p.showPage()
    p.save()

    return response

@login_required
def upload_medical_document(request):
    try:
        patient = PatientProfile.objects.get(user=request.user)
    except PatientProfile.DoesNotExist:
        messages.error(request, "Only patients can upload medical documents.")
        return redirect("home")

    if request.method == "POST":
        title = request.POST.get("title")
        document_type = request.POST.get("document_type")
        description = request.POST.get("description")
        file = request.FILES.get("file")

        if not title or not document_type or not file:
            messages.error(request, "Please fill title, document type, and upload a file.")
            return redirect("patient_dashboard")

        MedicalDocument.objects.create(
            patient=patient,
            title=title,
            document_type=document_type,
            description=description,
            file=file
        )

        messages.success(request, "Medical document uploaded successfully.")
        return redirect("patient_dashboard")

    return redirect("patient_dashboard")
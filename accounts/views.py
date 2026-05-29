from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

from accounts.models import DoctorProfile, PatientProfile
from appointments.models import MedicalHistory


def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect("custom_admin_dashboard")

            if DoctorProfile.objects.filter(user=user).exists():
                return redirect("doctor_dashboard")

            if PatientProfile.objects.filter(user=user).exists():
                return redirect("patient_dashboard")

            messages.error(request, "No doctor or patient profile found for this user.")
            return redirect("custom_login")

        messages.error(request, "Invalid username or password.")
        return redirect("custom_login")

    return render(request, "login.html")


def custom_logout(request):
    logout(request)
    return redirect("home")

def patient_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        phone = request.POST.get("phone")
        age = request.POST.get("age")
        gender = request.POST.get("gender")
        blood_group = request.POST.get("blood_group")

        disease_history = request.POST.get("disease_history")
        allergies = request.POST.get("allergies")
        current_medications = request.POST.get("current_medications")
        previous_surgeries = request.POST.get("previous_surgeries")
        notes = request.POST.get("notes")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("patient_signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another username.")
            return redirect("patient_signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        patient = PatientProfile.objects.create(
            user=user,
            phone=phone,
            age=age,
            gender=gender,
            blood_group=blood_group
        )

        MedicalHistory.objects.create(
            patient=patient,
            disease_history=disease_history,
            allergies=allergies,
            current_medications=current_medications,
            previous_surgeries=previous_surgeries,
            notes=notes
        )

        messages.success(request, "Signup successful. Please login.")
        return redirect("custom_login")

    return render(request, "patient_signup.html")
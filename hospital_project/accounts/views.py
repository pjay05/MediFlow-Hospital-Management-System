from django.shortcuts import render, redirect  # type: ignore[import]
from django.contrib.auth.models import User  # type: ignore[import]
from django.contrib.auth import authenticate, login, logout  # type: ignore[import]
from django.contrib import messages  # type: ignore[import]
from django.contrib.auth.decorators import login_required  # type: ignore[import]


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        user.save()

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, "signup.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def dashboard_view(request):
    return render(request, "dashboard.html")


from appointment.models import Doctor, Appointment, DoctorSlot, Hospital
from django.contrib.auth.decorators import login_required  # type: ignore[import]


def doctor_signup_view(request):
    hospitals = Hospital.objects.all()

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        hospital_id = request.POST.get("hospital")
        doctor_name = request.POST.get("doctor_name")
        specialization = request.POST.get("specialization")
        qualification = request.POST.get("qualification")
        experience = request.POST.get("experience")
        consultation_fee = request.POST.get("consultation_fee")
        phone = request.POST.get("phone")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("doctor_signup")

        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        hospital = Hospital.objects.get(id=hospital_id)

        Doctor.objects.create(
            user=user,
            hospital=hospital,
            doctor_name=doctor_name,
            specialization=specialization,
            qualification=qualification,
            experience=experience,
            consultation_fee=consultation_fee,
            email=email,
            phone=phone,
        )

        messages.success(request, "Doctor account created successfully. Please login.")
        return redirect("doctor_login")

    return render(request, "doctor_signup.html", {"hospitals": hospitals})


def doctor_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                Doctor.objects.get(user=user)
                login(request, user)
                return redirect("doctor_dashboard")
            except Doctor.DoesNotExist:
                messages.error(request, "This login is not registered as a doctor.")
                return redirect("doctor_login")
        else:
            messages.error(request, "Invalid doctor username or password.")
            return redirect("doctor_login")

    return render(request, "doctor_login.html")


@login_required
def doctor_dashboard_view(request):
    doctor = Doctor.objects.get(user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).order_by("-created_at")
    slots = DoctorSlot.objects.filter(doctor=doctor).order_by("-date")

    return render(
        request,
        "doctor_dashboard.html",
        {"doctor": doctor, "appointments": appointments, "slots": slots},
    )
